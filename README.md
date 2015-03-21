Fabric Vegetation
==========
Tool for generating virtual ivy around any given geometry, based-off a paper written by Bedřich Beneš (2002). Written for an industry masterclass using Fabric Engine 1.13.0, works in many DCC's but the UI is scripted for Maya 2014.

Requirements
--------------
Tested on Fabric Engine 1.13.0 which can be found here - http://dist.fabric-engine.com/FabricEngine/). A version of the Fabric:Splice node is included for 1.15.0 but requires manual set-up.

Usage
--------------
Simply clone the repo and add the 'ext' folder to the FABRIC_EXTS_PATH env variable.
Copy the files from inside the 'maya' folder to your 'maya/<version>-x64/scripts' folder and set up a shelf button to open the python interface to the Fabric:Splice node (an icon is provided in the images folder). The shelf button needs to include the python code:

```python
import FabricVegetation
FabricVegetation.FVegetationUI()
```

Various UI elements are explained in the following list, these values are also referenced in the documentation although under slightly different names.

* Distribution angle – The conical angle in which the bud can potentially grow to each step
* Distribution samples – The number of random positions the bud will evaluate against each step, the higher the more accurate the growth
* Bud chance – The chance of an inactive lateral bud being grown along a branch for traumatic reiteration-sakes
* Bud active chance – The chance of one of those inactive buds being active upon being created so as to achieve branching
* Leaf chance – The chance of a leaf being created per step, per branch
* Min increment size – The minimum distance each active bud has to grow per step
* Max increment size – The maximum distance each active bud can grow per step
* Increment steps – The number of iterations of growth to go through
* Max thickness – The maximum radius of the branching
* Leaf size – The size of each plane for the leaves
* Quadratic falloff lights – Whether the lights should have a quadratic falloff or not (doesn't work too well at the moment)

Current Issues
--------------
- Sunlight doesn't work very well, neither is the UI very prepared for artists to use it yet as there is no clear option and it doesn't check whether a sun already exists
- There is a bug mentioned in the documentation with the clear seeds and clear lights buttons, both of them disconnect all seeds and lights but don't clean the fabricVegetation node's multi-array indexes, making any new seeds/lights have bad naming convention and wrong connections
- The leaves are generally in the correct direction but there are cases where they may seem to be less random than desired, i.e. on a large flat surface, the sizes also need to be randomized
- There are occasional collisions with the environment geometry and the vegetation itself, however most of this should be fixed by now although the leaves do not have collision detection
- When there are no lights in the scene there is a strange bug that makes the vine grow wildly, nearly disregarding the environment geometry

References
--------------
Benes, B. and Millan, E. (2002). Virtual climbing plants competing for space. Proceedings of Computer Animation 2002 (CA 2002).