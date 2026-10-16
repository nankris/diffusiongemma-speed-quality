import pathlib,subprocess,shutil
R=pathlib.Path('/content/r027r')
if (R/'raw').exists():shutil.move(str(R/'raw'),str(R/'feasibility_raw'))
subprocess.Popen('nohup cmake --build /content/llama.cpp/build -j8 --target llama-server > /content/r027r/server_build.log 2>&1 &',shell=True)
print('server build launched; feasibility retained')
print((R/'probe.log').read_text())
for p in (R/'feasibility_raw').glob('000_ar.*'):print(p.name,p.read_text()[-2400:])
