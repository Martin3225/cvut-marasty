import os
import json
import shutil
from pathlib import Path

def process_questions():
    # Use absolute paths relative to the script location
    base_path = Path(__file__).parent.resolve()
    source_dir = base_path / 'questions'
    target_dir = base_path / 'web' / 'public' / 'subjects'
    subjects_json_path = base_path / 'web' / 'public' / 'subjects.json'

    # Clear target directory
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    subjects_list = []

    for subject_folder in source_dir.iterdir():
        if not subject_folder.is_dir():
            continue

        subject_code = subject_folder.name
        subject_json_src = subject_folder / 'subject.json'
        
        if not subject_json_src.exists():
            continue

        with open(subject_json_src, 'r', encoding='utf-8') as f:
            subject_data = json.load(f)

        # Create subject directory in public
        subject_target_dir = target_dir / subject_code
        subject_target_dir.mkdir(parents=True, exist_ok=True)

        all_subject_questions = []
        
        # Build master topic list from subject.json first
        subject_topics_list = subject_data.get('topics', [])
        topic_map = {t['id']: t['name'] for t in subject_topics_list}
        
        # 1. Process New Flat Structure (questions/subject/questions/id/)
        flat_questions_dir = subject_folder / 'questions'
        if flat_questions_dir.exists():
            for question_folder in sorted(flat_questions_dir.iterdir()):
                if not question_folder.is_dir() or question_folder.name.startswith('.'):
                    continue
                
                question_id = question_folder.name
                question_json_src = question_folder / 'question.json'
                if not question_json_src.exists():
                    continue

                with open(question_json_src, 'r', encoding='utf-8') as f:
                    q_content = json.load(f)

                # Images
                quiz_photo_exists = (question_folder / 'quiz.png').exists()
                photo_exists = (question_folder / 'photo.png').exists()

                # Paths are relative to public root in the browser
                question_public_path = f"subjects/{subject_code}/questions/{question_id}"
                
                # Metadata
                q_content['id'] = question_id
                q_content['subjectCode'] = subject_code
                
                # Support both 'topics' (preferred) and 'topic'
                if 'topics' not in q_content:
                    if 'topic' in q_content:
                        q_content['topics'] = [q_content['topic']]
                    else:
                        q_content['topics'] = []
                
                q_content['quizPhoto'] = f"{question_public_path}/quiz.png" if quiz_photo_exists else False
                q_content['photo'] = f"{question_public_path}/photo.png" if photo_exists else False

                if 'answers' in q_content:
                    for i, ans in enumerate(q_content['answers']):
                        ans['index'] = i + 1

                all_subject_questions.append(q_content)

                # Copy assets (only images, not question.json)
                target_q_dir = subject_target_dir / 'questions' / question_id
                target_q_dir.mkdir(parents=True, exist_ok=True)
                for item in question_folder.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        shutil.copy2(item, target_q_dir / item.name)

        # 2. Process Old Nested Structure (questions/subject/topic/id/)
        for topic_folder in sorted(subject_folder.iterdir()):
            if not topic_folder.is_dir() or topic_folder.name in ['.', '..', 'questions'] or topic_folder.name.startswith('.'):
                continue
                
            topic_id = topic_folder.name
            
            # If topic not in master list, try to find topic.json
            if topic_id not in topic_map:
                topic_name = topic_id
                topic_json_path = topic_folder / 'topic.json'
                if topic_json_path.exists():
                    try:
                        with open(topic_json_path, 'r', encoding='utf-8') as f:
                            t_data = json.load(f)
                            topic_name = t_data.get('name', topic_id)
                    except: pass
                
                topic_entry = {"id": topic_id, "name": topic_name}
                subject_topics_list.append(topic_entry)
                topic_map[topic_id] = topic_name
            
            for question_folder in sorted(topic_folder.iterdir()):
                if not question_folder.is_dir() or question_folder.name.startswith('.'):
                    continue
                
                question_id = question_folder.name
                
                # Skip if already processed in flat structure
                if any(q['id'] == question_id for q in all_subject_questions):
                    continue

                question_json_src = question_folder / 'question.json'
                if not question_json_src.exists():
                    continue

                with open(question_json_src, 'r', encoding='utf-8') as f:
                    q_content = json.load(f)
                
                quiz_photo_exists = (question_folder / 'quiz.png').exists()
                photo_exists = (question_folder / 'photo.png').exists()

                question_public_path = f"subjects/{subject_code}/topics/{topic_id}/{question_id}"
                
                q_content['id'] = question_id
                q_content['topics'] = [topic_id]
                q_content['subjectCode'] = subject_code
                q_content['quizPhoto'] = f"{question_public_path}/quiz.png" if quiz_photo_exists else False
                q_content['photo'] = f"{question_public_path}/photo.png" if photo_exists else False

                if 'answers' in q_content:
                    for i, ans in enumerate(q_content['answers']):
                        ans['index'] = i + 1

                all_subject_questions.append(q_content)
                
                target_q_dir = subject_target_dir / 'topics' / topic_id / question_id
                target_q_dir.mkdir(parents=True, exist_ok=True)
                for item in question_folder.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        shutil.copy2(item, target_q_dir / item.name)

        # Ensure subject_entry for global subjects.json
        subject_data['topics'] = subject_topics_list
        subject_entry = {
            "id": len(subjects_list) + 1,
            **subject_data,
            "code": subject_code
        }
        subjects_list.append(subject_entry)

        # Write subject.json to public
        with open(subject_target_dir / 'subject.json', 'w', encoding='utf-8') as f:
            json.dump(subject_data, f, indent=4, ensure_ascii=False)

        # Write questions.json to public
        with open(subject_target_dir / 'questions.json', 'w', encoding='utf-8') as f:
            json.dump({"questions": all_subject_questions}, f, indent=4, ensure_ascii=False)

    # Write overall subjects.json
    with open(subjects_json_path, 'w', encoding='utf-8') as f:
        json.dump({"subjects": subjects_list}, f, indent=4, ensure_ascii=False)

    print(f"Processed {len(subjects_list)} subjects.")

if __name__ == "__main__":
    process_questions()
