import os
import re

# TODO: Marissa needs to do the following:
#       4 - check in to git

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
for input_file in os.scandir(input_folder):
    if input_file.is_file():
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
        with open(input_file.path, 'r') as tf:
            # tf is just the variable name for the file, target file is the mnemonic
            for line in tf:
                # change from D-M-Y -> Y-M-D
                # capture groups are \N based on pattern matching in the first argument
                #   (anything wrapped in parentheses is matched)
                re_line = re.sub(r"(.*),(\d+)/(\d+)/(\d+),(.*)", r"\1,20\4-\3-\2T\5", line)

                rf.write(re_line)

                # only want to show a brief example of how we are changing the input file on stdout
                if line_count < 2:
                    print('[INFO]: pre-sub, post-sub\n\t', line, '\t', re_line)
                # iterate line_count so we don't print out the entire file
                line_count += 1
        print('[INFO]: Done parsing', input_file.path)
        # best practice is to close file handlers when done
        rf.close()
    else:
        print('[WARNING]: Skipping parsing ', input_file.path, '(not a file)')
