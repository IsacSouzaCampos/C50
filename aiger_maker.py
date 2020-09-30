import os


source_path = 'sop_pos_mux/original'
target_path = 'sop_pos_mux/aiger'

file = open(f'{target_path.split("/")[0]}/mltest.txt', 'w+')
file.truncate(0)
file.close()

for file_name in os.listdir(source_path):
    if '.eqn' not in file_name:
        continue
    script = f'read_eqn {source_path}/{file_name}\nstrash\nwrite_aiger {target_path}/{file_name.replace(".eqn", ".aig")};' \
             f'&read {target_path}/{file_name.replace(".eqn", ".aig")}; &ps; &mltest ../Benchmarks/{file_name.replace(".eqn", ".valid.pla")}'
    file = open('script.scr', 'w+')
    file.write(script)
    file.close()

    os.system(f'.././abc -c "source script.scr" >> {target_path.split("/")[0]}/mltest.txt')
