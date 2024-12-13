import time
import re
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/makeCall', methods=['POST'])
def makeDailyCall():
    try:
        driver = webdriver.Edge()
        data = request.get_json()
        driver.get("https://fateconline.com.br")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "txtEmail"))
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "txtSenha"))
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "btnLogar"))
        )

        userEmail = "..."
        userPassword = "..."
        driver.find_element(By.ID, "txtEmail").send_keys(userEmail)
        driver.find_element(By.ID, "txtSenha").send_keys(userPassword)
        driver.find_element(By.ID, "btnLogar").click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "textoMenuSecundario")),
        )

        driver.get("https://www.fateconline.com.br/sistema/Paginas/Professores/Chamada/Chamada.aspx")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "body_ddlSemestreAno")),
        )

        class_name_dropdown_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ddlTurmas")),
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "txtData")),
        )

        hour_dropdown_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ddlInicio")),
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "btnGerar")),
        )

        select_class = Select(class_name_dropdown_element)
        class_name = data.get('className').upper()
        className = re.sub(r'[^A-Z]', '', class_name)

        for class_option in select_class.options:
            option = re.sub(r'[^A-Z]', '', class_option.text).upper().split(' - ')[0]
            if className in option:
                class_option.click()
                break

        select_class = Select(hour_dropdown_element)

        for class_option in select_class.options:
            if data.get('hour') in class_option.text:
                class_option.click()
                break

        driver.find_element(By.ID, "btnGerar").click()

        student_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row.bg-white.clicarimg"))
        )

        student_danger_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row.bg-danger.clicarimg"))
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "txtConteudo")),
        )

        students = []
        for student_element in student_elements:
            full_text = student_element.text
            print(f"Full text: {full_text}")
            if " - RA:" in full_text:
                student_name = full_text.split(" - RA: F")[0]
                student_ra = full_text.split(" - RA: F")[1] .split('\n')[0]
                students.append({'name': student_name, 'ra': student_ra})

        students_danger = []
        for student_element in student_danger_elements:
            full_text = student_element.text
            print(f"Full text: {full_text}")
            if " - RA:" in full_text:
                student_name = full_text.split(" - RA: F")[0]
                student_ra = full_text.split(" - RA: F")[1] .split('\n')[0]
                students_danger.append({'name': student_name, 'ra': student_ra})

        filtered_student_ras = [student for student in students if student.get('ra') not in data.get('studentsRas')]
        filtered_student_danger_ras = [student for student in students_danger if student.get('ra') in data.get('studentsRas')]

        sorted_students = sorted(filtered_student_ras + filtered_student_danger_ras, key=lambda student: student['name'])

        for student in sorted_students:
            student_element = driver.find_element(By.XPATH, f"//strong[contains(text(), '{student.get('ra')}')]")
            student_element.click()
            print(f"Clicked on student: {student.get('ra')}")

        time.sleep(2)
    finally:
        message = "Lista de Presença gerada por AI Class Tracker RPA - Confirme abaixo"
        oldMessage = driver.find_element(By.ID, "txtConteudo")

        if oldMessage.text in '':
            oldMessage.send_keys(message)
        else:
            oldMessage.send_keys(' | ' + message)
        input()
        return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
