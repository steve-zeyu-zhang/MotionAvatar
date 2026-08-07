cd checkpoints

cd t2m 
echo -e "Downloading evaluation models for HumanML3D dataset"
wget https://github.com/steve-zeyu-zhang/data/releases/download/momask/humanml3d_evaluator.zip
echo -e "Unzipping humanml3d_evaluator.zip"
unzip humanml3d_evaluator.zip

echo -e "Clearning humanml3d_evaluator.zip"
rm humanml3d_evaluator.zip

cd ../kit/
echo -e "Downloading pretrained models for KIT-ML dataset"
wget https://github.com/steve-zeyu-zhang/data/releases/download/momask/kit_evaluator.zip

echo -e "Unzipping kit_evaluator.zip"
unzip kit_evaluator.zip

echo -e "Clearning kit_evaluator.zip"
rm kit_evaluator.zip

cd ../../

echo -e "Downloading done!"