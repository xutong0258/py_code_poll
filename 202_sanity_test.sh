test=`cat /home/yskj/data/test_flag.yaml`
echo $test
new_string=$(echo "$test" | tr -d '[:space:]')
if echo "$new_string" | grep -q "START"; then
    echo "already START, return"
    exit 0
else
    echo "OK, start now"
fi

python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '202' SANITY_TEST
cd /home/yskj/data/se-autotest-237/sanity_cases/3_product && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/0_face_mode && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/1_free_mode && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/2_we_chat/21_run_50_MULTI_8 && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/2_we_chat/22_run_distance && pytest --html=report/report.html
cd /home/yskj/data/se-autotest-237/sanity_cases/2_we_chat/23_run_circle/1_circle && pytest --html=report/report.html
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '202' SANITY_TEST

python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '202' FOUL_FACE_TEST
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
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '202' FOUL_FACE_TEST

python3.10 /home/yskj/data/se-autotest-237/util/start_msg.py '202' FOUL_FREE_TEST
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
python3.10 /home/yskj/data/se-autotest-237/util/end_msg.py '202' FOUL_FREE_TEST
