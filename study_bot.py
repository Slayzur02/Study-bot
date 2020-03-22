from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib.request, json
import time
import requests
import sys
import simpleaudio as sa
import random as random



# plays music, will be used if there is a problem when filling in the questions
def call_music(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    for _ in range(2):
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing


# store into questions_and_answer
class q_and_a:
    def __init__(self, questionID, question_text, answer_dictionary):
        self.questionID = questionID
        self.question_text = question_text
        self.answer_dictionary = answer_dictionary
    
    def set_questionID(self, questionID):
        self.questionID = questionID
    
    def set_question_text(self, question_text):
        self.question_text = question_text
    
    def set_answer_dictionary(self, answer_dictionary):
        self.answer_dictionary = answer_dictionary

# store answers in q_and_a
class answer:
    def __init__(self,answerID, answer_text, correct):
        self.answerID = answerID
        self.answer_text = answer_text
        self.correct = correct

    def set_answerID(self, answerID):
        self.answerID = answerID

    def set_answer_text(self, answer_text):
        self.answer_text = answer_text

    def set_correct(self, correct):
        self.correct = correct


# store for testing_list
class testing_q_and_a:
    def __init__(self, questionID, answerID):
        self.test_questionID = questionID
        self.test_answerID = answerID
    def set_test_questionID(self, questionID):
        self.test_questionID = questionID
    def set_test_answerID(self, answerID):
        self.test_answerID = answerID




class study_bot:
    #is shared between instances so that I can create a second bot that uses the answers from the first bot.
    #holds q_and_a, update after every test
    questions_and_answers = {
        # questionID: {
        #   "questionID": questionID,
        #   "question_text": question_text,
        #   "answer_dictionary": {
        #       answerID: {
        #           "answerID",
        #           "answer_text",
        #           "correct"
        #       }
        # }    
        # }
    } 
    def __init__(self, username, password, site_url, test_id, filename, bugged, testing_list, time_range):
        self.username = username
        self.password = password
        self.site_url = site_url
        self.test_id = test_id
        self.filename = filename
        self.bugged = bugged
        self.time_range = time_range

        #holds testing_q_and_a, is looped through to update questions_and_answers
        self.testing_list = testing_list
        
        _browser_profile = webdriver.FirefoxProfile()
        # Make no notifications pop-up, which can stop certain buttons
        _browser_profile.set_preference("dom.webnotifications.enabled", False)
        self.bot = webdriver.Firefox(firefox_profile=_browser_profile)

    def login(self):
        bot = self.bot
        bot.get("website-route")
        time.sleep(3)
        site_username = bot.find_element_by_id('UserName')
        site_password = bot.find_element_by_id('Password')
        site_login_click = bot.find_element_by_id('AjaxLogin')
        site_username.clear()
        site_password.clear()
        site_username.send_keys(self.username)
        site_password.send_keys(self.password)
        site_login_click.send_keys(Keys.RETURN)

    def reset_testing_list(self):
        self.testing_list = []

    def get_into_test(self):
        bot = self.bot
        bot.get("due-to-confidential-reasons-I-cannot-show-the-website-name")
        time.sleep(5)
        bot.get(self.site_url)
        time.sleep(5)
        site_vao_thi_button = bot.find_element_by_css_selector('.btn.btn-primary')
        site_vao_thi_button.send_keys(Keys.RETURN)
        time.sleep(5)
        site_bat_dau_lam_bai_button = bot.find_element_by_css_selector('.btn.btn-warning.btn-start-test')
        site_bat_dau_lam_bai_button.send_keys(Keys.RETURN)

    # Puts all the questions and answers into a map
    def query_questions_and_answers(self):
        bot = self.bot
        questions_and_answers_list = bot.find_elements_by_css_selector('.question-box')
        for question_and_answer in questions_and_answers_list:
            #get the question ID and store into q_and_a instance
            q_and_a_instance = q_and_a("","",{})
            questionID = question_and_answer.get_attribute("id")
            q_and_a_instance.set_questionID(questionID)

            #get the question Text and store into q_an_a instance
            question_text_element = question_and_answer.find_element_by_css_selector('.col-11')
            question = question_text_element.text
            q_and_a_instance.set_question_text(question)

            # (use for) get the answerID - answerText and store them into answer dictionary and store answer_dic to q_and_a_dictionary
            answer_elements = question_and_answer.find_elements_by_css_selector('.col-md-6')
            for answer_element in answer_elements:
                answer_instance = answer("", "", "")
                # get answer ID
                answer_id_element = answer_element.find_element_by_tag_name('input')
                answerID = answer_id_element.get_attribute("id")
                answer_instance.set_answerID(answerID)

                # get answer text
                answer_text_element = answer_element.find_element_by_css_selector('.col-10')
                answer_text = answer_text_element.text
                answer_instance.set_answer_text(answer_text)

                q_and_a_instance.answer_dictionary[answer_instance.answerID] = {
                    "answerID": answer_instance.answerID,
                    "answer_text": answer_instance.answer_text,
                    "correct": "",
                }

            # store to questions_and_answers
            if q_and_a_instance.questionID in study_bot.questions_and_answers:
                continue
            else:
                study_bot.questions_and_answers[q_and_a_instance.questionID] = {
                    "questionID": q_and_a_instance.questionID,
                    "question_text": q_and_a_instance.question_text,
                    "answer_dictionary": q_and_a_instance.answer_dictionary,
                    "correct_answer_id": "",
                }
            
        

    def choose_answers_and_submit(self):
        bot = self.bot
        questions_and_answers_list = bot.find_elements_by_css_selector('.question-box')

        # Use for loop to get all the elements of the questions
        for question_and_answer in questions_and_answers_list:

            # scroll into question so I can click it
            question_and_answer.location_once_scrolled_into_view

            # get questionID
            testing_q_and_a_instance = testing_q_and_a("", "")
            questionID = question_and_answer.get_attribute("id")
            testing_q_and_a_instance.set_test_questionID(questionID)

            # get all the answer elements
            answer_elements = question_and_answer.find_elements_by_css_selector('.col-md-6')

            # if the question already has an answer - choose the correct answer:
            if study_bot.questions_and_answers[questionID]["correct_answer_id"] != "":
                correct_answer_id = study_bot.questions_and_answers[questionID]["correct_answer_id"]
                for answer_element in answer_elements:
                    answer_id_element = answer_element.find_element_by_tag_name('input')
                    answerID = answer_id_element.get_attribute("id")
                    if answerID != correct_answer_id:
                        continue
                    else:
                        answer_id_element.location_once_scrolled_into_view
                        answer_id_element.click() 
                        testing_q_and_a_instance.set_test_answerID(answerID)
                        break

            # if it does not have an answer, choose the one that hasn't been checked, a.k.a correct = false
            else:
                for answer_element in answer_elements:
                    answer_id_element = answer_element.find_element_by_tag_name('input')
                    answerID = answer_id_element.get_attribute("id")
                    if study_bot.questions_and_answers[questionID]["answer_dictionary"][answerID]["correct"] != "":
                        continue
                    else:
                        answer_id_element.location_once_scrolled_into_view
                        answer_id_element.click()
                        testing_q_and_a_instance.set_test_answerID(answerID)
                        break
            
            # Append to the test_list with dictionary as above

            self.testing_list.append({
                "test_questionID": testing_q_and_a_instance.test_questionID,
                "test_answerID": testing_q_and_a_instance.test_answerID,
                "correct": False,
            })


        time.sleep(1)
        # Scroll to the "Submit" button
        bot.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        nop_bai_button = bot.find_element_by_css_selector('.btn.btn-warning')
        nop_bai_button.click()
        time.sleep(1)

        dong_y_button = bot.find_element_by_css_selector('.swal2-confirm')
        dong_y_button.send_keys(Keys.RETURN)
        
    
    def reflect_answers(self):
        bot = self.bot
        
        cookies = bot.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        r = s.get('website-route-json-api'+self.test_id+'&rt=1')
        if r.status_code == 200:
            true_answers_list = r.json()['TrueAnswer'].split(',')

        # changes all "correct" = True based on the index of the list
        def return_index(ket_qua_string): 
            string_number_with_dot = ket_qua_string.strip().split(' ')[1]
            number = int(string_number_with_dot[:-1])
            return number-1
        true_answers_index = list(map(return_index, true_answers_list))

        for i in true_answers_index:
            self.testing_list[i]["correct"] = True
        
        # Update the questions_and_answers based on testing_list
        for node in self.testing_list:
            if node["correct"]: 
                correct_questionID = node["test_questionID"]

                if study_bot.questions_and_answers[correct_questionID]["correct_answer_id"] == "":
                    study_bot.questions_and_answers[correct_questionID]["correct_answer_id"] = node["test_answerID"]
                    study_bot.questions_and_answers[correct_questionID]["answer_dictionary"][node["test_answerID"]]["correct"] = "true"
                if correct_questionID in self.bugged:
                    self.bugged.remove(correct_questionID)
            else: 
                wrong_questionID = node["test_questionID"]
                if study_bot.questions_and_answers[wrong_questionID]["correct_answer_id"] == "":
                    study_bot.questions_and_answers[wrong_questionID]["answer_dictionary"][node["test_answerID"]]["correct"] = "false"
                    

        sys.stdout.flush()


    def identify_bugged_questions(self):
        self.bugged = []
        for val in study_bot.questions_and_answers.values():
            if val["correct_answer_id"] == "":
                for v in val["answer_dictionary"].values():
                    v["correct"] = ""
                self.bugged.append(v["questionID"])
    
    def fix_bugged_questions(self):
        bot = self.bot
        questions_and_answers_list = bot.find_elements_by_css_selector('.question-box')

        for question_and_answer in questions_and_answers_list:
            question_and_answer.location_once_scrolled_into_view

            # get questionID
            testing_q_and_a_instance = testing_q_and_a("", "")
            questionID = question_and_answer.get_attribute("id")
            if questionID not in self.bugged:
                continue
            
            testing_q_and_a_instance.set_test_questionID(questionID)

            # get all the answer elements
            answer_elements = question_and_answer.find_elements_by_css_selector('.col-md-6')

            # It does not have an answer, choose the one that hasn't been checked, a.k.a correct = false
            for answer_element in answer_elements:
                answer_id_element = answer_element.find_element_by_tag_name('input')
                answerID = answer_id_element.get_attribute("id")
                if study_bot.questions_and_answers[questionID]["answer_dictionary"][answerID]["correct"] != "":
                    continue
                else:
                    answer_id_element.click()
                    testing_q_and_a_instance.set_test_answerID(answerID)
                    break
            
            # Append to the test_list with dictionary as above
            self.testing_list.append({
                "test_questionID": testing_q_and_a_instance.test_questionID,
                "test_answerID": testing_q_and_a_instance.test_answerID,
                "correct": False,
            })


        time.sleep(1)
        # Scroll to the "Submit" button
        bot.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)


        nop_bai_button = bot.find_element_by_css_selector('.btn.btn-warning')
        nop_bai_button.click()
        time.sleep(1)

        dong_y_button = bot.find_element_by_css_selector('.swal2-confirm')
        dong_y_button.send_keys(Keys.RETURN)


    # Called once we have a question map. Tests and re-evaluates.
    def final_check(self):
        bot = self.bot
        wrong_questions = []

        for _ in range(3):
            time.sleep(10)
            self.testing_list = []
            self.get_into_test()
            time.sleep(10)
            
            self.choose_answers_and_submit()
            time.sleep(10)
        
            # Retrieve the json in route-under-website using request
            cookies = bot.get_cookies()
            s = requests.Session()
            for cookie in cookies:
                s.cookies.set(cookie['name'], cookie['value'])
            r = s.get('route-under-main-website'+self.test_id+'&rt=1')
            if r.status_code == 200:
                wrong_answers_list = r.json()['FalseAnser'].split(',')

            # checks if there are no wrong answers (a.k.a wrong_answer_list = [''])
            if wrong_answers_list[0] == '':
                continue

            # there are wrong answers, so push the questions IDs into the wrong_questions list
            def return_index(ket_qua_string): 
                string_number_with_dot = ket_qua_string.strip().split(' ')[1]
                number = int(string_number_with_dot[:-1])
                return number-1
            wrong_answers_index = list(map(return_index, wrong_answers_list))

            for i in wrong_answers_index:
                wrong_questions.append(self.testing_list[i]["test_questionID"])
            time.sleep(10)

        # if no wrong question appears at least twice (out of three times) - it's fine
        if len(wrong_questions) == len(set(wrong_questions)):
            return False
        # else, push it into bugged_questions and call fix_bugged_questions to solve
        else:
            for node in wrong_questions:
                wrong_questions.remove(node)
                if node in wrong_questions:
                    self.bugged.append(node)
                    while node in wrong_questions:
                        wrong_questions.remove(node)
            while len(self.bugged) > 0:
                self.testing_list = []
                self.fix_bugged_questions()
                self.reflect_answers()
            return True
    

    def log_the_answers(self):
        file=open(self.filename+".txt", "w+")
        i=0
        for value in study_bot.questions_and_answers.values():
            question_text = value["question_text"]
            j=0
            list_of_choices = ["", "", "", ""]
            for v in value["answer_dictionary"].values():
                j+=1
                list_of_choices[j-1] = v["answer_text"]
            answer_text = value["answer_dictionary"][value["correct_answer_id"]]["answer_text"]
            answerID =value["answer_dictionary"][value["correct_answer_id"]]["answerID"] 
            i += 1
            file.write(f"Cau hoi {i}: \n {question_text} \nLua chon 1:{list_of_choices[0]}\nLua chon 2:{list_of_choices[1]}\nLua chon 3:{list_of_choices[2]}\nLua chon 4: {list_of_choices[3]}\n    Cau tra loi: {answer_text} \n    answerID: {answerID}  \n \n \n")
        file.close()

    def destroy_self(self):
        bot = self.bot
        bot.quit()

    def answering_test(self):
        bot = self.bot
        questions_and_answers_list = bot.find_elements_by_css_selector('.question-box')

        # Use for loop to get all the elements of the questions
        for question_and_answer in questions_and_answers_list:

            # scroll into question so I can click it
            question_and_answer.location_once_scrolled_into_view

            # get questionID
            questionID = question_and_answer.get_attribute("id")

            # get all the answer elements
            answer_elements = question_and_answer.find_elements_by_css_selector('.col-md-6')

            # if the question already has an answer - choose the correct answer:
            if study_bot.questions_and_answers[questionID]["correct_answer_id"] != "":
                correct_answer_id = study_bot.questions_and_answers[questionID]["correct_answer_id"]
                for answer_element in answer_elements:
                    answer_id_element = answer_element.find_element_by_tag_name('input')
                    answerID = answer_id_element.get_attribute("id")
                    if answerID != correct_answer_id:
                        continue
                    else:
                        answer_id_element.location_once_scrolled_into_view
                        answer_id_element.click() 
                        break

            # if it does not have an answer, alert with bug and open music file.
            else:
                print("THERE WAS A BUG - returning...")
                call_music("beep_warning.wav")
                time.sleep(300)

        call_music("finished_script.wav")
        random_wait_time = random.randint(60*self.time_range[0], 60*self.time_range[1])
        print("RANDON WAIT TIME:" + str(random_wait_time))
        time.sleep(random_wait_time)
        # Scroll to the "Submit" button
        bot.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)

        nop_bai_button = bot.find_element_by_css_selector('.btn.btn-warning')
        nop_bai_button.click()
        time.sleep(3)

        dong_y_button = bot.find_element_by_css_selector('.swal2-confirm')
        dong_y_button.send_keys(Keys.RETURN)

# This is the original code that runs only once. Has been refactored into the function below  

# create_study_bot = study_bot("", "", "route-under-website", "test", "test-name", [])
# create_study_bot.login()
# time.sleep(1)
# create_study_bot.get_into_test()
# time.sleep(6)
# create_study_bot.query_questions_and_answers()
# time.sleep(4)
# create_study_bot.choose_answers_and_submit()
# time.sleep(10)
# create_study_bot.reflect_answers()
# time.sleep(6)

# create_study_bot.reset_testing_list()
# create_study_bot.get_into_test()
# time.sleep(6)
# create_study_bot.choose_answers_and_submit()
# time.sleep(10)
# create_study_bot.reflect_answers()
# time.sleep(6)


# create_study_bot.reset_testing_list()
# create_study_bot.get_into_test()
# time.sleep(6)
# create_study_bot.choose_answers_and_submit()
# time.sleep(10)
# create_study_bot.reflect_answers()
# time.sleep(6)

# create_study_bot.reset_testing_list()
# create_study_bot.get_into_test()
# time.sleep(6)
# create_study_bot.choose_answers_and_submit()
# time.sleep(10)
# create_study_bot.reflect_answers()
# time.sleep(6)
# create_study_bot.reset_testing_list()

# create_study_bot.identify_bugged_questions()
# while len(create_study_bot.bugged) > 0:
#     "THERE WAS A BUGG"
#     create_study_bot.reset_testing_list()
#     create_study_bot.fix_bugged_questions()
#     create_study_bot.reflect_answers()

# while create_study_bot.final_check():
#     pass


# create_study_bot.log_the_answers()



def giai_nhieu_de(site, id, filename, time_range):
    try:
        study_bot.questions_and_answers = {}
        create_study_bot = study_bot("testing_id", "testing_id", site, id, filename, [], [], time_range)
        create_study_bot.login()
        time.sleep(1)
        create_study_bot.get_into_test()
        time.sleep(6)
        create_study_bot.query_questions_and_answers()
        time.sleep(4)
        create_study_bot.choose_answers_and_submit()
        time.sleep(10)
        create_study_bot.reflect_answers()
        time.sleep(6)

        create_study_bot.reset_testing_list()
        create_study_bot.get_into_test()
        time.sleep(6)
        create_study_bot.choose_answers_and_submit()
        time.sleep(10)
        create_study_bot.reflect_answers()
        time.sleep(6)


        create_study_bot.reset_testing_list()
        create_study_bot.get_into_test()
        time.sleep(6)
        create_study_bot.choose_answers_and_submit()
        time.sleep(10)
        create_study_bot.reflect_answers()
        time.sleep(6)

        create_study_bot.reset_testing_list()
        create_study_bot.get_into_test()
        time.sleep(6)
        create_study_bot.choose_answers_and_submit()
        time.sleep(10)
        create_study_bot.reflect_answers()
        time.sleep(6)
        create_study_bot.reset_testing_list()

        create_study_bot.identify_bugged_questions()
        while len(create_study_bot.bugged) > 0:
            create_study_bot.reset_testing_list()
            create_study_bot.fix_bugged_questions()
            create_study_bot.reflect_answers()

        # calls final_check till everything is correct (or "almost" correct)
        while create_study_bot.final_check():
            pass

        # create_study_bot.log_the_answers()

        time.sleep(5)
        

        answering_study_bot = study_bot("your-main-id", "your-main-id", site, id, "dont-use", [], [], time_range)
        answering_study_bot.login()
        time.sleep(2)
        answering_study_bot.get_into_test()
        time.sleep(5)
        answering_study_bot.answering_test()

        time.sleep(14)

        # create_study_bot.destroy_self()
        # answering_study_bot.destroy_self()

        call_music("finished_script.wav")
    except Exception as e: 
        print("A random error occured")
        call_music("beep_warning.wav")
        print(e)





giai_nhieu_de("website-route", "test-id", "test-name", [15, 20]) 
