import streamlit as st
import fitz  # PyMuPDF
import re

def extract_questions_from_pdf(uploaded_file):
    pdf_document = fitz.open(stream=uploaded_file.read())
    extracted_text = [page.get_text() for page in pdf_document]
    pdf_document.close()

    question_pattern = re.compile(
        r'(\d+\)) (.*?) \nA\) (.*?) \nB\) (.*?) \nC\) (.*?) \nD\) (.*?) \nE\) (.*?) \nAnswer:\s+([A-E]) ',
        re.DOTALL
    )

    questions_data = []
    for page_text in extracted_text:
        questions = question_pattern.findall(page_text)
        for question in questions:
            question_dict = {
                'question_number': question[0].strip(')'),
                'question': question[1].strip(),
                'options': {
                    'A': question[2].strip(),
                    'B': question[3].strip(),
                    'C': question[4].strip(),
                    'D': question[5].strip(),
                    'E': question[6].strip()
                },
                'answer': question[7].strip()
            }
            questions_data.append(question_dict)

    return questions_data

def main():
    st.title('GT-R Game')

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        questions = extract_questions_from_pdf(uploaded_file)
        if questions:
            st.session_state.questions = questions 
            st.success('Questions extracted! Please select a range to start the game.')

    if 'questions' in st.session_state and st.session_state.questions:
        total_questions = len(st.session_state.questions)
        st.write(f"Total questions extracted: {total_questions}")
        start_range = st.number_input('Start from question number', min_value=1, max_value=total_questions, value=1)
        batch_size = st.number_input('Number of questions to play', min_value=1, max_value=total_questions - start_range + 1, value=10)
        load_questions = st.button('Load Questions')

        if load_questions or 'current_batch' in st.session_state:
            if load_questions:
                st.session_state.current_batch = st.session_state.questions[start_range - 1: start_range - 1 + batch_size]

            for i, q in enumerate(st.session_state.current_batch, start=start_range):
                with st.form(key=str(i)):
                    st.write(f"Question {i}: {q['question']}")
                    options = q['options']
                    answer = st.radio("Choices", options.keys(), format_func=lambda x: options[x], key=f"answer_{i}")
                    submitted = st.form_submit_button("Submit Answer")
                    if submitted:
                        if answer == q['answer']:
                            st.success(f"Correct! The answer is {q['answer']}.")
                            st.session_state.questions[int(q['question_number']) - 1]['attempted'] = 'correct'
                        else:
                            st.error(f"Wrong! The correct answer was {q['answer']}.")
                            st.session_state.questions[int(q['question_number']) - 1]['attempted'] = 'wrong'

            correct_answers = sum(1 for q in st.session_state.questions if q.get('attempted') == 'correct')

            if any('attempted' in q for q in st.session_state.questions):
                st.write(f"Score: {correct_answers} correct answers out of {len(st.session_state.current_batch)} attempted.")

if __name__ == "__main__":
    main()
