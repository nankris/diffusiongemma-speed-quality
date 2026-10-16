cd /content; B=/content/llama.cpp/build/bin
DG=$(ls /content/m/dg/*.gguf); G4=$(ls /content/m/g4/*.gguf)
echo "DG=$DG G4=$G4"
timeout 600 $B/llama-diffusion-cli -m $DG -ngl 99 -n 256 -p "Explain in three sentences why the sky is blue." > /content/r027/smoke_dg.out 2> /content/r027/smoke_dg.err
echo "dg exit $?"
