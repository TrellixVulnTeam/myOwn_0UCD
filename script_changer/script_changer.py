refact_line = []
temp_text_list = []

file_name = str(input('Enter valid name of file (for example: example.txt): '))

with open(file_name, 'r') as f:
    for line in f.readlines():       
        temp_text_list.append(line.split())

for line in temp_text_list:  
    # print(line)
    for refact_line in line:
        if ('cast(' or 'typing.cast(') in refact_line:
            # print(f"My line - {refact_line}")
            
            last_string = line[line.index(refact_line) + 1]
            last_string = last_string[:-1]
            line[line.index(refact_line) + 1] = last_string
            line.pop(line.index(refact_line))
            
                    
            # print(f"My refactored line - {refact_line}")
            
            
# print(temp_text_list)

main_text = ''
for item in temp_text_list:
    main_text += " ".join(item)
    main_text += '\n'
    
# print(main_text)

with open(file_name, 'w') as f:
    for line in main_text:       
        f.write(line)
    print('Cast lines were changed.')
