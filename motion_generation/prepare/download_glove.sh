echo -e "Downloading glove (in use by the evaluators, not by MoMask itself)"
wget https://github.com/steve-zeyu-zhang/data/releases/download/momask/glove.zip
rm -rf glove

unzip glove.zip
echo -e "Cleaning\n"
rm glove.zip

echo -e "Downloading done!"