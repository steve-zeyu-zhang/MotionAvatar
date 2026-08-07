# Truebones Zoo — 65-Animal Training Partition

The synthesis pipeline trains **one SinMDM model per motion clip** (878 clips across 65 animal
categories from the Truebones Zoo dataset). To parallelize this on a cluster,
the 65 animals were partitioned into 15 groups and each group was trained as an
independent job (`sequential_training.py` run on that group's BVH folder).

This table documents the exact partition used for the paper. The raw Truebones
`.bvh`/`.fbx` files are commercially licensed and cannot be redistributed here
(see *Data preparation* in the main README for how to obtain them).

| Group | Animals | # Motions |
|---|---|---|
| Group1 | Spider, Stego, Tricera, Tukan, Turtle, Tyranno | 62 |
| Group2 | Rat, Rhino, Roach, SandMouse, Scorpion, Skunk | 58 |
| Group3 | Raindeer, Raptor, SabreToothTiger | 63 |
| Group4 | Parrot, Pigeon, Pirrana, PolarBear, Pteranodon, Puppy | 60 |
| Group5 | Lion, Lynx, Mammoth, Monkey, Ostrich | 61 |
| Group6 | Isopetra, Jaguar, Jaws, KingCobra, Leapord | 54 |
| Group7 | HermitCrab, Hippopotamus, Horse, Hound | 64 |
| Group8 | Elephant, Flamingo, Fox, Gazelle, Giantbee, Goat, Hamster | 61 |
| Group9 | Deer, Dragon, Eagle, FireAnt | 64 |
| Group10 | Coyote, Crow, Dog | 63 |
| Group11 | Centipede, Chicken, Comodoa, Crab, Cricket, Crocodile | 56 |
| Group12 | Bat, Buffalo, Buzzard, Camel, Cat | 58 |
| Group13 | Ant, Bear, Bird | 64 |
| Group14 | Trex | 72 |
| Group15 | Anaconda | 18 |
| **Total** | **65 animals** | **878** |

Notes:

- Animal names follow the Truebones file-name prefixes (`Animal-Action.bvh`),
  including their original spellings (e.g. `Leapord`, `Comodoa`, `Raindeer`,
  `Pirrana`).
- `output.csv` at the repository root is the full 878-row manifest
  (Animal, Motion Name, file name) of the filtered dataset.
