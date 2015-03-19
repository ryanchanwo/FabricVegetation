# module FabricVegetation

import maya.cmds as cmds
from functools import partial

'''
  Quick a dirty UI mockup, ignoring efficiency/modularity, just to give an idea
  of how the artist would be able to use the Fabric:Splice node without needing
  to access the node graph/write any expressions, etc.
'''

## Get the currently selected items and check their type against the given string
#  @param objType The string to specify what type the selection should be
def grabSelection(objType) :
  # grab the current selection
  selected=cmds.ls(sl=1)

  # check if anything is selected
  if len(selected)==0 :
    print 'FVegetation: Nothing is selected.'
    return None

  for i in range(0, len(selected)) :
    # condition for if not checking for a group node
    check=selected[i]
    if objType is not 'transform' :
      check=cmds.listRelatives(selected[i])
      if len(check)>1 :
        print 'FVegetation: Delete history on mesh before connecting.'
        return None

    # check that the selection is of correct type
    if cmds.nodeType(check) not in objType :
      print 'FVegetation: Selected object is not a '+objType+'.'
      return None

  return selected

## Clean method of disconnecting multiple sources from a multi-array attribute
#  @param attrib The name of the multi-array attribute
def disconnectMultiAttrib(attrib) :
  # check if the attribute has any connections and exit if none
  multiLen=cmds.getAttr('fabricVegetation.'+attrib, size=True)

  if multiLen==0:
    print 'FVegetation: No inputs to disconnect for '+attrib+'.'
    return 1

  # otherwise disconnect all the incoming connections
  for i in range(0, multiLen) :
    # currently there is a bug where the seeds aren't cleared completely
    cmds.removeMultiInstance('fabricVegetation.'+attrib+'['+str(i)+']', b=True)

  return 0

## Creates and imports the FVegetation splice node
def importSplice(*args) :
  # check if there is an existing splice node
  if cmds.objExists('fabricVegetation') :
    print 'FVegetation: Fabric:Splice node already exists!'
    return

  # create the node and load in the splice file
  node=cmds.createNode('spliceMayaNode')
  cmds.rename(node, 'fabricVegetation')
  path=cmds.internalVar(userScriptDir=True)+'FabricVegetation/FabricVegetation.splice'
  cmds.fabricSplice('loadSplice', 'fabricVegetation', '{"fileName" : "'+path+'"}')

## Select the FVegetation splice node
def selectSplice(*args) :
  cmds.select('fabricVegetation', replace=True)

## Connect any number of arbitrary meshes to the FVegetation splice node
#  @param environment The mesh to which to connect, either collision or shadowing
def connectMeshes(environment, *args) :
  mesh=[]

  # make some alterations to the selection group for speedtree meshes
  if cmds.checkBoxGrp('speedtree', q=True, v1=True)==True :
    root=grabSelection('transform')
    # give an error if the selection isn't a root group
    if 'tree' not in root[0] :
      print 'FVegetation: Speedtree root group not selected.'
      return

    # find all the shape nodes, ignoring all 'group' relatives
    shapeNodes=cmds.listRelatives(root, ad=1, typ='shape')
    # check for omission strings to selectively connect the speedtree mesh
    omit=cmds.textField(environment+'Omit', q=True, text=True)
    omitList=omit.split(' ')

    tree=[]
    for i in range(0, len(shapeNodes)) :
      # skip any of the nodes with the omission strings in
      if len(omit)>0 :
        skip=False
        for j in range(0, len(omitList)) :
          if omitList[j] in shapeNodes[i] :
            skip=True
            break

        if skip==True :
          continue

      # otherwise place the node in a list
      tree.append(shapeNodes[i])

    # update the mesh list with the selected shape nodes
    mesh=tree

  else :
    mesh=grabSelection('mesh')
    # exit if a mesh isn't returned
    if mesh is None :
      return

  # attach the given meshes
  for i in range(0, len(mesh)) :
    environmentCap=environment.capitalize()
    envLen=cmds.getAttr('fabricVegetation.env'+environmentCap, size=True)
    append=environmentCap+'['+str(envLen)+']'
    cmds.connectAttr(mesh[i]+'.outMesh', 'fabricVegetation.env'+append)

  print 'FVegetation: Connected '+str(len(mesh))+' mesh(es) to '+environment+' input.'

## Disconnect all the meshes from the FVegetation splice node
def disconnectMeshes(*args) :
  collide=disconnectMultiAttrib('envCollide')
  shadow=disconnectMultiAttrib('envShadow')
  if collide==0 and shadow==0 :
    print 'FVegetation: Disconnected input collision and shadowing meshes.'

## Toggle the FVegetation splice node to have it prepare acceleration structures
def prepareMeshes(*args) :
  cmds.setAttr('fabricVegetation.prepareMeshes', 1)

## Enable and disable UI elements depending on whether or not the connecting mesh is a speedtree
def toggleSpeedtreeVars(*args) :
  if cmds.checkBoxGrp('speedtree', q=True, v1=True) :
    cmds.text('collideText', e=True, enable=True)
    cmds.text('shadowText', e=True, enable=True)
    cmds.textField('collideOmit', e=True, enable=True)
    cmds.textField('shadowOmit', e=True, enable=True)

  else :
    cmds.text('collideText', e=True, enable=False)
    cmds.text('shadowText', e=True, enable=False)
    cmds.textField('collideOmit', e=True, enable=False)
    cmds.textField('shadowOmit', e=True, enable=False)

## Create and connect a locator as a seed for the vegetation
def createSeed(*args) :
  # find other seeds in the scene to find the number
  seedLen=cmds.getAttr('fabricVegetation.seeds', size=True)
  seed='seed'+str(seedLen)+'_LOC'
  cmds.spaceLocator(name=seed)
  cmds.connectAttr(seed+'.worldPosition[0]', 'fabricVegetation.seeds['+str(seedLen)+']')

## Connect only a locator to the FVegetation splice node
def connectSeed(*args) :
  seed=grabSelection('locator')
  if seed is None :
    return

  seedLen=cmds.getAttr('fabricVegetation.seeds', size=True)
  cmds.connectAttr(seed[0]+'.worldPosition[0]', 'fabricVegetation.seeds['+str(seedLen)+']')

## Clear out all connections with seeds to the FVegetation splice node
#  @note There is a bug with this, it disconnects the seeds, but doesn't remove the multi-array index!
def clearSeeds(*args) :
  seed=disconnectMultiAttrib('seeds')
  if seed==0 :
    print 'FVegetation: Disconnected all seeds.'

## Create and connect a point light as a light source for the vegetation
def createLight(*args) :
  posLen=cmds.getAttr('fabricVegetation.lightPos', size=True)
  intLen=cmds.getAttr('fabricVegetation.lightInt', size=True)
  light='light'+str(posLen)+'_LGT'
  cmds.pointLight(name=light)
  cmds.connectAttr(light+'.translate', 'fabricVegetation.lightPos['+str(posLen)+']')
  cmds.connectAttr(light+'.intensity', 'fabricVegetation.lightInt['+str(intLen)+']')

  print 'FVegetation: Created and connected '+light+'.'

## Connect only a point light to the FVegetation splice node
def connectLight(*args) :
  light=grabSelection('pointLight')
  if light is None :
    return

  posLen=cmds.getAttr('fabricVegetation.lightPos', size=True)
  intLen=cmds.getAttr('fabricVegetation.lightInt', size=True)
  cmds.connectAttr(light[0]+'.translate', 'fabricVegetation.lightPos['+str(posLen)+']')
  cmds.connectAttr(light[0]+'.intensity', 'fabricVegetation.lightInt['+str(intLen)+']')

  print 'FVegetation: Connected '+light[0]+'.'

## Clear out all connections with lights to the FVegetation splice node
#  @note There is a bug with this, it disconnects the lights, but doesn't remove the multi-array index!
def clearLights(*args) :
  posVal=disconnectMultiAttrib('lightPos')
  intVal=disconnectMultiAttrib('lightInt')
  if posVal==0 and intVal==0 :
    print 'FVegetation: Disconnected all lights.'

## Create and connect an ambient light as the sunlight source for the vegetation
def createSun(*args) :
  cmds.ambientLight(name='sun_LGT', intensity=0)
  cmds.connectAttr('sun_LGT.translate', 'fabricVegetation.sunPos')

  print 'FVegetation: Created and connected sun location.'

## Query all the relevant UI slider values and set the node attributes accordingly
def update(*args) :
  # blindly update the settings and prepare everything other than the main loop itself
  distribution=cmds.intSliderGrp('distribution', q=True, value=True)
  samples=cmds.intSliderGrp('samples', q=True, value=True)
  budChance=cmds.floatSliderGrp('budChance', q=True, value=True)
  branchChance=cmds.floatSliderGrp('branchChance', q=True, value=True)
  leafChance=cmds.floatSliderGrp('leafChance', q=True, value=True)
  minStep=cmds.floatSliderGrp('minStep', q=True, value=True)
  maxStep=cmds.floatSliderGrp('maxStep', q=True, value=True)
  steps=cmds.intSliderGrp('steps', q=True, value=True)
  quadratic=cmds.checkBoxGrp('quadratic', q=True, v1=True)

  branchThick=cmds.floatSliderGrp('branchThick', q=True, value=True)
  leafSize=cmds.floatSliderGrp('leafSize', q=True, value=True)

  cmds.setAttr('fabricVegetation.distribution', distribution)
  cmds.setAttr('fabricVegetation.samples', samples)
  cmds.setAttr('fabricVegetation.budChance', budChance)
  cmds.setAttr('fabricVegetation.branchChance', branchChance)
  cmds.setAttr('fabricVegetation.leafChance', leafChance)
  cmds.setAttr('fabricVegetation.minStep', minStep)
  cmds.setAttr('fabricVegetation.maxStep', maxStep)
  cmds.setAttr('fabricVegetation.steps', steps)
  cmds.setAttr('fabricVegetation.quadratic', quadratic)

  cmds.setAttr('fabricVegetation.branchThick', branchThick)
  cmds.setAttr('fabricVegetation.leafSize', leafSize)

## Toggle the FVegetation splice node to have it grow the vegetation
def grow(*args) :
  # check if there is a mesh attached, if not create and attach it
  mesh=cmds.connectionInfo('fabricVegetation.vegeBranches', dfs=True)
  if len(mesh)==0 :
    nodeBranches=cmds.createNode('mesh')
    nodeLeaves=cmds.createNode('mesh')
    transformBranches=cmds.listRelatives(nodeBranches, children=False, parent=True)
    transformLeaves=cmds.listRelatives(nodeLeaves, children=False, parent=True)
    cmds.rename(transformBranches, 'vege_Branches_GEO')
    cmds.rename(transformLeaves, 'vege_Leaves_GEO')
    cmds.connectAttr('fabricVegetation.vegeBranches', 'vege_Branches_GEO.inMesh')
    cmds.connectAttr('fabricVegetation.vegeLeaves', 'vege_Leaves_GEO.inMesh')

  cmds.setAttr('fabricVegetation.buildGrowth', 1)

## Create a UI for the artist to access and effect node elements easily
def FVegetationUI() :
  # main window setup
  uiTitle='Fabric Vegetation'
  if cmds.dockControl('fabricVegetationDock', exists=True) :
    cmds.deleteUI('fabricVegetationDock')

  window=cmds.window(title=uiTitle)
  scroll=cmds.scrollLayout(verticalScrollBarThickness=10)
  mainLayout=cmds.columnLayout(parent=scroll,
                               backgroundColor=[0.2, 0.2, 0.2],
                               columnWidth=340,
                               columnAttach=['both', 30],
                               columnAlign='center',
                               rowSpacing=7)

  cmds.separator(style='none', height=20, parent=mainLayout)

  path=cmds.internalVar(userScriptDir=True)+'FabricVegetation/images/FabricVegetationBanner.png'
  cmds.image(parent=mainLayout, image=path)

  cmds.separator(style='none', height=7, parent=mainLayout)

  nodeLayout=cmds.rowLayout(parent=mainLayout,
                            numberOfColumns=2,
                            columnWidth2=[140, 140],
                            columnAttach2=['left', 'right'],
                            columnAlign2=['center', 'center'])
  nodeLeft=cmds.columnLayout(parent=nodeLayout,
                             columnWidth=130,
                             columnAttach=['both', 5],
                             rowSpacing=7)
  nodeRight=cmds.columnLayout(parent=nodeLayout,
                             columnWidth=130,
                             columnAttach=['both', 5],
                             rowSpacing=7)
  cmds.button(parent=nodeLeft, label='Add Splice Node', height=25,
              command=importSplice)
  cmds.button(parent=nodeRight, label='Select Node', height=25,
              command=selectSplice)

  cmds.separator(style='in', height=20, parent=mainLayout)

  cmds.text('Growth Properties', parent=mainLayout, font='boldLabelFont')
  cmds.separator(style='none', height=3, parent=mainLayout)

  # could not be bothered with attaching functions to changecommand flag
  # to make the sliders automatically update the splice node's values
  cmds.intSliderGrp('distribution', parent=mainLayout, label='Distribution Angle', field=True,
                    min=0, fmn=0, max=90, fmx=90, value=30,
                    columnAttach=[1, 'left', 0],
                    columnWidth3=[100, 50, 100])
  cmds.intSliderGrp('samples', parent=mainLayout, label='Distribution Samples', field=True,
                    min=0, fmn=0, max=64, fmx=256, value=32,
                    columnAttach=[1, 'left', 0],
                    columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('budChance', parent=mainLayout, label='Bud Chance', field=True,
                      min=0, fmn=0, max=0.2, fmx=0.5, step=0.05, value=0.05,
                      columnAttach=[1, 'left', 0],
                      columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('branchChance', parent=mainLayout, label='Bud Active Chance', field=True,
                      min=0, fmn=0, max=0.5, fmx=1.0, step=0.05, value=0.1,
                     columnAttach=[1, 'left', 0],
                     columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('leafChance', parent=mainLayout, label='Leaf Chance', field=True,
                      min=0, fmn=0, max=0.6, fmx=1.0, step=0.1, value=0.2,
                      columnAttach=[1, 'left', 0],
                      columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('minStep', parent=mainLayout, label='Min Increment Size', field=True,
                      min=0.005, fmn=0.005, max=0.5, fmx=0.5, step=0.005, value=0.002,
                      columnAttach=[1, 'left', 0],
                      columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('maxStep', parent=mainLayout, label='Max Increment Size', field=True,
                    min=0.2, fmn=0.2, max=1.0, fmx=2.0, step=0.005, value=0.5,
                    columnAttach=[1, 'left', 0],
                    columnWidth3=[100, 50, 100])
  cmds.intSliderGrp('steps', parent=mainLayout, label='Increment Steps', field=True,
                    min=0, fmn=0, max=2000, fmx=3000, value=600,
                    columnAttach=[1, 'left', 0],
                    columnWidth3=[100, 50, 100])
  cmds.separator(style='none', height=3, parent=mainLayout)
  cmds.checkBoxGrp('quadratic', label='Quadratic Falloff Lights', parent=mainLayout,
                   columnAttach=[2, 'left', 10],
                   columnWidth2=[160, 50])

  cmds.separator(style='none', height=10, parent=mainLayout)

  cmds.text('Appearance Properties', parent=mainLayout, font='boldLabelFont')
  cmds.separator(style='none', height=3, parent=mainLayout)

  cmds.floatSliderGrp('branchThick', parent=mainLayout, label='Max Thickness', field=True,
                      min=0.01, fmn=0.01, max=0.2, fmx=0.5, step=0.005, value=0.06,
                      columnAttach=[1, 'left', 0],
                      columnWidth3=[100, 50, 100])
  cmds.floatSliderGrp('leafSize', parent=mainLayout, label='Leaf Size', field=True,
                      min=0.2, fmn=0.2, max=1.0, fmx=2.0, step=0.1, value=0.6,
                      columnAttach=[1, 'left', 0],
                      columnWidth3=[100, 50, 100])

  cmds.separator(style='none', height=10, parent=mainLayout)

  cmds.button(parent=mainLayout, label='Update Settings',
              backgroundColor=[0.25, 0.25, 0.25], height=25,
              command=update)

  cmds.separator(style='in', height=20, parent=mainLayout)

  cmds.text('External Attributes', parent=mainLayout, font='boldLabelFont')
  cmds.separator(style='none', height=3, parent=mainLayout)

  attribsLayout=cmds.rowLayout(parent=mainLayout,
                               numberOfColumns=2,
                               columnWidth2=[140, 140],
                               columnAttach2=['left', 'right'],
                               columnAlign2=['center', 'center'])
  attribsLeft=cmds.columnLayout(parent=attribsLayout,
                                columnWidth=130,
                                columnAttach=['both', 5],
                                rowSpacing=7)
  attribsRight=cmds.columnLayout(parent=attribsLayout,
                                 columnWidth=130,
                                 columnAttach=['both', 5],
                                 rowSpacing=7)

  cmds.text('Seeds', parent=attribsLeft)
  cmds.button(parent=attribsLeft, label='Create', height=25,
              command=createSeed)
  cmds.button(parent=attribsLeft, label='Connect', height=25,
              command=connectSeed)
  cmds.button(parent=attribsLeft, label='Clear', height=25,
              command=clearSeeds)
  cmds.text('Lights', parent=attribsRight)
  cmds.button(parent=attribsRight, label='Create', height=25,
              command=createLight)
  cmds.button(parent=attribsRight, label='Connect', height=25,
              command=connectLight)
  cmds.button(parent=attribsRight, label='Clear', height=25,
              command=clearLights)

  cmds.button(parent=mainLayout, label='Create Sun', height=25,
              command=createSun)

  cmds.separator(style='in', height=20, parent=mainLayout)

  cmds.text('Mesh Connections', parent=mainLayout, font='boldLabelFont')
  cmds.text('Select any abstract mesh before connecting.', parent=mainLayout)

  cmds.separator(style='none', height=10, parent=mainLayout)

  cmds.checkBoxGrp('speedtree', label='Speedtree Mesh', parent=mainLayout,
                   columnAttach=[2, 'left', 10],
                   columnWidth2=[160, 50],
                   changeCommand=toggleSpeedtreeVars)
  cmds.text('(Speedtree note: select root group before connecting.)', parent=mainLayout)

  cmds.separator(style='none', height=7, parent=mainLayout)

  meshLayout=cmds.rowLayout(parent=mainLayout,
                            numberOfColumns=2,
                            columnWidth2=[140, 140],
                            columnAttach2=['left', 'right'],
                            columnAlign2=['center', 'center'])
  meshLeft=cmds.columnLayout(parent=meshLayout,
                             columnWidth=130,
                             columnAttach=['both', 5],
                             rowSpacing=7)
  meshRight=cmds.columnLayout(parent=meshLayout,
                              columnWidth=130,
                              columnAttach=['both', 5],
                              rowSpacing=7)

  cmds.text('collideText', label='Collision Omissions', parent=meshLeft)
  cmds.textField('collideOmit', parent=meshLeft, placeholderText='leaf')
  cmds.button(parent=meshLeft, label='Connect to\nCollision Mesh', height=35,
              command=partial(connectMeshes, 'collide'))
  cmds.text('shadowText', label='Shadowing Omissions', parent=meshRight)
  cmds.textField('shadowOmit', parent=meshRight, placeholderText='leaf twig')
  cmds.button(parent=meshRight, label='Connect to\nShadowing Mesh', height=35,
              command=partial(connectMeshes, 'shadow'))

  toggleSpeedtreeVars()

  cmds.separator(style='none', height=10, parent=mainLayout)

  connectLayout=cmds.rowLayout(parent=mainLayout,
                               numberOfColumns=2,
                               columnWidth2=[140, 140],
                               columnAttach2=['left', 'right'],
                               columnAlign2=['center', 'center'])
  connectLeft=cmds.columnLayout(parent=connectLayout,
                                columnWidth=130,
                                columnAttach=['both', 5],
                                rowSpacing=7)
  connectRight=cmds.columnLayout(parent=connectLayout,
                                 columnWidth=130,
                                 columnAttach=['both', 5],
                                 rowSpacing=7)
  cmds.button(parent=connectLeft, label='Prepare Meshes',
              backgroundColor=[0.25, 0.25, 0.25], height=25,
              command=prepareMeshes)
  cmds.button(parent=connectRight, label='Clear Inputs', height=25,
              command=disconnectMeshes)

  cmds.separator(style='in', height=20, parent=mainLayout)

  cmds.button(parent=mainLayout, label='Grow',
              backgroundColor=[0.25, 0.25, 0.25], height=35,
              command=grow)

  cmds.separator(style='none', height=20, parent=mainLayout)

  # show the window as a dockable object
  cmds.dockControl('fabricVegetationDock',
                   area='left',
                   content=window,
                   allowedArea=['right', 'left'],
                   label=uiTitle,
                   width=366,
                   sizeable=False)