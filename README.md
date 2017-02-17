# Vegetation

Tool for generating ivy around a given piece of geometry. The implementation is based-off
**Virtual climbing plants competing for space** by Bedřich Beneš (2002). Written for an industry
masterclass using [Fabric Engine](http://fabricengine.com/) 1.13.0. This should grant us
DCC-agnosticism out-of-the-box, but the GUI is only compatible with Maya.

## Requirements

- Fabric Engine: 1.13.0.
- Maya: 2014.

## Installation

### For the splice tool

Simply clone the repo and add the `ext` directory to the `FABRIC_EXTS_PATH` environment variable.

### For the GUI

Copy the files from inside the `maya` directory to your `maya/<VERSION>-x64/scripts` folder and
set up a shelf button to open the GUI to the Fabric Splice node (an icon is provided in the
`images` directory). Add the following Python code to the shelf button:

```python
import FabricVegetation
FabricVegetation.FVegetationUI()
```

## Usage

Various options in the GUI are explained in the following list. These values are also referenced
in the documentation although under slightly different names.

- *Distribution angle:* Conical angle within which the bud may grow at each step.
- *Distribution samples:* Number of random positions the bud will evaluate against at each step.
The higher the value, the more accurate the growth.
- *Bud chance:* Chance for an inactive lateral bud to grow along a branch for traumatic
reiteration-sakes.
- *Bud active chance:* Chance for an inactive bud to activate upon being created, so as to achieve
branching.
- *Leaf chance:* Chance for a leaf to be created at each step, per-branch.
- *Min increment size:* Minimum distance each active bud has to grow per-step.
- *Max increment size:* Maximum distance each active bud can grow per-step.
- *Increment steps:* Number of iterations of growth to simulate.
- *Max thickness:* Maximum radius of the branching.
- *Leaf size:* Size of each plane geometry for the leaves.
- *Quadratic falloff lights:* Whether the lights should have a quadratic falloff or not
(does not work too well at the moment).

## Known Issues

- The GUI is quite rudimentary, it was done *quickly and dirtily* with Maya GUI commands.
- Sunlight does not work entirely as expected.
- The clear seeds and clear lights buttons disconnect all seeds and lights, but do not clean the
fabricVegetation node's multi-array indices. This causes any new seeds/lights to have a bad
naming convention and incorrect connections.
- The leaves are generally in the correct direction, but there are cases where they may seem to
be less random than desired, i.e. on a large flat surface, the sizes also need to be randomized.
- There are occasional collisions with the environment geometry and the vegetation itself.
- Leaves do not have psuedo-collision detection like the ivy.
- When there are no lights in the scene there is a strange bug that makes the vine grow wildly,
nearly disregarding the environment geometry.

## References

Benes, B. and Millan, E. (2002). Virtual climbing plants competing for space. Proceedings of
Computer Animation 2002 (CA 2002).
