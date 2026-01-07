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

        topics_data = {"topics": {}}
        
        # Build topics from folders and their topic.json
        subject_topics_list = []
        
        # Sort topic folders to have consistent output
        for topic_folder in sorted(subject_folder.iterdir()):
            if not topic_folder.is_dir() or topic_folder.name.startswith('.'):
                continue
                
            topic_id = topic_folder.name
            
            # Read topic name from topic.json if it exists
            topic_name = topic_id
            topic_json_path = topic_folder / 'topic.json'
            if topic_json_path.exists():
                try:
                    with open(topic_json_path, 'r', encoding='utf-8') as f:
                        t_data = json.load(f)
                        topic_name = t_data.get('name', topic_id)
                except Exception as e:
                    print(f"Error reading {topic_json_path}: {e}")

            subject_topics_list.append({
                "id": topic_id,
                "name": topic_name
            })
            
            topics_data["topics"][topic_id] = {"questions": []}
            
            # Sort question folders
            for question_folder in sorted(topic_folder.iterdir()):
                if not question_folder.is_dir() or question_folder.name.startswith('.'):
                    continue
                
                question_json_src = question_folder / 'question.json'
                if not question_json_src.exists():
                    continue
                
                question_id = question_folder.name
                topics_data["topics"][topic_id]["questions"].append(question_id)
                
                # Create target question directory
                question_target_dir = subject_target_dir / 'topics' / topic_id / question_id
                question_target_dir.mkdir(parents=True, exist_ok=True)
                
                # Check for images and update question.json content
                quiz_photo_exists = (question_folder / 'quiz.png').exists()
                photo_exists = (question_folder / 'photo.png').exists()

                with open(question_json_src, 'r', encoding='utf-8') as f:
                    q_content = json.load(f)
                
                q_content['quizPhoto'] = quiz_photo_exists
                q_content['photo'] = photo_exists

                # Write modified question.json to target
                with open(question_target_dir / 'question.json', 'w', encoding='utf-8') as f:
                    json.dump(q_content, f, indent=4, ensure_ascii=False)

                # Copy other files (photos)
                for item in question_folder.iterdir():
                    # We exclude question.json (wrote it above) and topic.json
                    if item.is_file() and item.name not in ['question.json', 'topic.json']:
                        shutil.copy2(item, question_target_dir / item.name)

        # Ensure subject_data has the latest topics info
        subject_data['topics'] = subject_topics_list
        with open(subject_target_dir / 'subject.json', 'w', encoding='utf-8') as f:
            json.dump(subject_data, f, indent=4, ensure_ascii=False)

        # Update subject_entry for the global subjects.json
        subject_entry = {
            "id": len(subjects_list) + 1,
            **subject_data,
            "code": subject_code
        }
        subjects_list.append(subject_entry)

        # Write questions.json for the subject
        with open(subject_target_dir / 'questions.json', 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, indent=4, ensure_ascii=False)

    # Write overall subjects.json
    with open(subjects_json_path, 'w', encoding='utf-8') as f:
        json.dump({"subjects": subjects_list}, f, indent=4, ensure_ascii=False)

    print(f"Processed {len(subjects_list)} subjects.")

if __name__ == "__main__":
    process_questions()
