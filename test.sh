#echo TARGET_SERVER: '237' > /home/yskj/data/target_server.yaml
python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '237' SANITY_TEST
cd /home/yskj/data/se-autotest-237/sanity_cases/0_face_mode && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/1_free_mode && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/2_we_chat && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/3_product && pytest --html=report/report.html
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '237' SANITY_TEST

python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '237' FOUL_FACE_TEST
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/01_stand_jump && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/05_rope_skip && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/06_50m_run && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/09_solid_ball && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/04_sit_forward/sit_forward_foul_001 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/04_sit_forward/sit_forward_foul_002 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/04_sit_forward/sit_forward_foul_005 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/03_sit_up/sit_up_foul_001 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/03_sit_up/sit_up_foul_002 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/03_sit_up/sit_up_foul_003 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/03_sit_up/sit_up_foul_004 && pytest --html=report/report.html
# cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/02_pull_up && pytest --html=report/report.html
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '237' FOUL_FACE_TEST

python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '237' FOUL_FREE_TEST
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/01_stand_jump && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/05_rope_skip/rope_skip_foul_001 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/06_50m_run && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/09_solid_ball && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/04_sit_forward/sit_forward_foul_001 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/04_sit_forward/sit_forward_foul_002 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/0_face_mode/04_sit_forward/sit_forward_foul_005 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/03_sit_up/sit_up_foul_001 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/03_sit_up/sit_up_foul_002 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/03_sit_up/sit_up_foul_003 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/03_sit_up/sit_up_foul_004 && pytest --html=report/report.html
# cd /home/yskj/data/se-autotest-237/foul_cases/1_free_mode/02_pull_up && pytest --html=report/report.html
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '237' FOUL_FREE_TEST
