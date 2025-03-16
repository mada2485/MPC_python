import os
import re
import datetime

# @name parse_to_datetime
# @args
#   str_datetime - a string containing a date / time to be converted
# @returns
#   returns a datetime.datetime object
# @notes
#   this is the datetime format as defined here:
#   https://docs.python.org/3/library/datetime.html#format-codes
def parse_to_datetime(str_datetime):
    # example:
    #  Sun Feb 16 2025 22:48:25 GMT-0700
    str_datetime_fmt = "%a %b %d %Y %H:%M:%S %Z%z"
    return datetime.datetime.strptime(str_datetime, str_datetime_fmt)

# @name parse_from_datetime
# @args
#   datetime_obj - a datetime.datetime object
# @returns
#   returns a formatted string for the preferred logging format
def parse_from_datetime(datetime_obj):
    # example:
    #  2025-02-14T08:50:26
    str_datetime_fmt = "%Y-%m-%dT%H:%M:%S"
    return datetime_obj.strftime(str_datetime_fmt)

# TODO: print out system path for the input_folder and output_folder
input_folder  = 'input'
output_folder = 'output'

# TODO: if the directory does not exist for input, error out

# if the directory does not exist for output, create it
if not os.path.exists(output_folder):
    print('[INFO]: output folder does not exist, creating', output_folder)
    os.makedirs(output_folder, exist_ok=True)

# going to read through all files in the input_folder and output_folder variables
#   (you can rename these to pick a different input / output folder)
# this has been updated to only accept .csv files (was picking up .swp files from vim)
for input_file in os.scandir(input_folder):
    if input_file.is_file() and input_file.path.endswith('.csv'):
        print('[INFO]: Starting parsing', input_file.path)
        output_file_path = os.path.join(output_folder, input_file.name)
        print('[INFO]: Writing to', output_file_path)
        # rf is regex file mnemonic (this is not the ideal way to open files, but we are
        #   writing and not reading, so who cares)
        rf = open(output_file_path, 'w')
        # INFO: line_count is just used to make sure we don't flood stdout with
        #       every possible print statement - just want to give some insight to
        #       the user what we are doing
        line_count = 0
        irregular_line_count = 0
        # the following could be done with just an integer, but the boolean
        #   may make it easier to understand
        was_last_irregular = False
        sequential_irregular = 0

        with open(input_file.path, 'r') as tf:
            # tf is just the variable name for the file, target file is the mnemonic
            for line in tf:
                # going to turn one line into multiple, based on how many data points are in each capture
                # first up is a hash and a timestamp, so let's extract that
                # example:
                #  "e00fce68c7197b6d5c8bc47e",Sun Feb 16 2025 22:48:25 GMT-0700 (Mountain Standard Time),"[[ 
                #    so to parse this, we look for whatever garbage, then a close quote comma to signify the end of device id
                #    and then we grab everything before the timezone in parantheses. timezone changes, the word Time doesn't seem to
                re_line_ts = re.sub(r"^.*\",(.*) \(.*Time\).*", r"\1", line).strip()
                line_base_ts = parse_to_datetime(re_line_ts)
                # line_count is used in a few places to prevent us from doing a bunch of stdout that floods it all
                if line_count < 3:
                    print("[INFO]: timestamp found: ", re_line_ts)
                    print("[INFO]: timestamp parsed to: ", parse_from_datetime(line_base_ts))

                # for some reason - there are two kinds of lines we can encounter.
                #   so we can use the presence of the "[[" substring to tell what we're dealing with
                if "[[" in line :
                    # capture groups are \N based on pattern matching in the first argument
                    #   (anything wrapped in parentheses is matched)
                    #re_line = re.sub(r"(.*),(\d+)/(\d+)/(\d+),(.*)", r"\1,20\4-\3-\2T\5", line)
                    re_line = re.sub(r"^.*\"\[\[(.*)\]\].*", r"\1", line)

                    data_entries = re_line.split('],[')
                    data_entry_i = 0
                    for data_entry in data_entries:
                        # now that we have the entries, let's split the entities into a list, 
                        #   remove all of the spacing, and get ready to re-write to file
                        data_entry_split = data_entry.split(',')
                        data_entry_split = map(str.strip, data_entry_split)
                        data_entry_split_str = ','.join(data_entry_split)
                        # for multiple entries (i.e. this loop, we add ~11 seconds between them
                        #   as per the logging interval determined in the feather's firmware
                        data_entry_ts = line_base_ts + datetime.timedelta(0,(11 * data_entry_i))
                        data_entry_ts_str = parse_from_datetime(data_entry_ts)
                        # now make the string we want to print from the others we've parsed in this loop already
                        data_entry_string = "%s,%s" %(data_entry_ts_str,data_entry_split_str)

                        # now write the result out
                        rf.write((data_entry_string + '\n'))

                        # only want to show a brief example of how we are changing the input file on stdout
                        if line_count < 2:
                            print(("[%02d]" %(data_entry_i + 1)), data_entry_string)
                        # increment our data_entry_i index / counter
                        data_entry_i  += 1
                    # update boolean to indicate we are not in the irregular entries anymore
                    was_last_irregular = False
                else :
                    if irregular_line_count < 2 :
                        print('[WARNING]: found irregular line - ', line.strip())

                    # important that this section is done at the "top" of the loop, for how it's written
                    if was_last_irregular : 
                        # found another one in this section
                        sequential_irregular += 1
                    else : 
                        # update boolean to indicate we just parsed an irregular line for the first time in a bit
                        was_last_irregular = True
                        # we set this to 0, as we so far have 1-in-a-row - this needs to be reset back down or we will
                        #   continue to increment it between sections and screw things up
                        sequential_irregular = 0

                    re_line = re.sub(r"^.*\",.* \(.*Time\),", r"", line).strip()
                    # these irregular lines don't seem to have whitespace to strip, so we're good to take this as-is
                    data_entry_str = re_line
                    # correctly offset the timestamp
                    data_entry_ts = line_base_ts + datetime.timedelta(0,(11 * sequential_irregular))
                    data_entry_ts_str = parse_from_datetime(data_entry_ts)
                    # construct the entry string
                    data_entry_string = "%s,%s" %(data_entry_ts_str,data_entry_str)

                    # now write the result out, preview the first few irregular lines,
                    #   this is done regardless of line_count, could probably be improved there
                    if irregular_line_count < 2 :
                        print('[INFO]: irregular preview', sequential_irregular, '-',  data_entry_string)
                    rf.write((data_entry_string + '\n'))

                    # for warning messages, keep track of the number of times we do things this way
                    irregular_line_count += 1

                # iterate line_count so we don't print out the entire file
                line_count += 1
        if irregular_line_count > 0 :
            print('[WARNING]: Found %d irregular lines in %s' %(irregular_line_count, input_file.path))
        print('[INFO]: Done parsing', input_file.path)
        # best practice is to close file handlers when done
        rf.close()
    else:
        print('[WARNING]: Skipping parsing ', input_file.path, '(not a file)')
