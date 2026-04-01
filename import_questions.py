from config.question import quiz_data
result =""
i=1
for quiz in quiz_data:
    options = "'["
    j=1
    for option in quiz['options']:
        if len(quiz['options']) == j:
            options += f'"{option}"'
        else:
            options += f'"{option}",'
        j+=1
    options += "]'"
    result +=f'({i}, "{quiz['question']}", {options}, {quiz['correct_option']}),\n'
    i += 1
print(result)

