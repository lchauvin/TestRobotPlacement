import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# TestRobotPlacement
#

class TestRobotPlacement:
  def __init__(self, parent):
    parent.title = "TestRobotPlacement" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Laurent Chauvin (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.  and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['TestRobotPlacement'] = self.runTest

  def runTest(self):
    tester = TestRobotPlacementTest()
    tester.runTest()

#
# qTestRobotPlacementWidget
#

class TestRobotPlacementWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "TestRobotPlacement Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Model: ", self.inputSelector)

    #
    # Sphere model
    #
    self.sphereModel = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
    self.sphereModel.SetName("SphereModel")
    slicer.mrmlScene.AddNode(self.sphereModel)
    
    displayNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelDisplayNode")
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.SetOpacity(0.35)
    displayNode.SetColor(1.0,0.0,0.0)
    self.sphereModel.SetAndObserveDisplayNodeID(displayNode.GetID())

    #
    # Seed point
    #
    self.sphereSeedListSelector = slicer.qMRMLNodeComboBox()
    self.sphereSeedListSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.sphereSeedListSelector.baseName = "SeedPoint"
    self.sphereSeedListSelector.selectNodeUponCreation = True
    self.sphereSeedListSelector.addEnabled = True
    self.sphereSeedListSelector.removeEnabled = True
    self.sphereSeedListSelector.noneEnabled = False
    self.sphereSeedListSelector.showHidden = False
    self.sphereSeedListSelector.showChildNodeTypes = False
    self.sphereSeedListSelector.setMRMLScene( slicer.mrmlScene )
    self.sphereSeedListSelector.setToolTip( "Seed list" )
    parametersFormLayout.addRow("Seed Point: ", self.sphereSeedListSelector)

    #
    # Sphere radius
    #
    self.sphereRadiusSliderWidget = ctk.ctkSliderWidget()
    self.sphereRadiusSliderWidget.singleStep = 1.0
    self.sphereRadiusSliderWidget.minimum = 1.0
    self.sphereRadiusSliderWidget.maximum = 100.0
    self.sphereRadiusSliderWidget.value = 40.0
    self.sphereRadiusSliderWidget.setToolTip("Set sphere radius in mm.")
    parametersFormLayout.addRow("Sphere Radius (mm)", self.sphereRadiusSliderWidget)
    
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.sphereSeedListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSeedListChanged)
    self.sphereRadiusSliderWidget.connect("valueChanged(double)", self.updateSphere)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSeedListChanged(self):
    seedList = self.sphereSeedListSelector.currentNode()
    seedList.AddObserver(seedList.PointModifiedEvent, self.onMarkupModified)

  def onMarkupModified(self,obj,callData):
    if self.sphereModel == None:
      self.sphereModel = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
      self.sphereModel.SetName("SphereModel")
      slicer.mrmlScene.AddNode(self.sphereModel)

      displayNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelDisplayNode")
      slicer.mrmlScene.AddNode(displayNode)
      displayNode.SetOpacity(0.35)
      displayNode.SetColor(1.0,0.0,0.0)
      self.sphereModel.SetAndObserveDisplayNodeID(displayNode.GetID())
      
    self.updateSphere(self.sphereRadiusSliderWidget.value)  

  def updateSphere(self,radius):    
    sphereCenter = [0.0, 0.0, 0.0]
    if self.sphereSeedListSelector.currentNode():
      self.sphereSeedListSelector.currentNode().GetNthFiducialPosition(0,sphereCenter)

    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(sphereCenter)
    sphere.SetThetaResolution(20)
    sphere.SetPhiResolution(20)
    sphere.SetRadius(radius)
    sphere.Update()
    
    self.sphereModel.SetAndObservePolyData(sphere.GetOutput())
    self.sphereModel.Modified()

  def onApplyButton(self):
    logic = TestRobotPlacementLogic()
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.sphereModel, self.sphereSeedListSelector.currentNode())

  def onReload(self,moduleName="TestRobotPlacement"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="TestRobotPlacement"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# TestRobotPlacementLogic
#

class TestRobotPlacementLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == -1:
      # full window
      widget = slicer.util.mainWindow()
    elif type == slicer.qMRMLScreenShotDialog().FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog().ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog().Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog().Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog().Green:
      # green slice window
      widget = lm.sliceWidget("Green")

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self,inputModel,sModel,seedList):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    tri = vtk.vtkDelaunay3D()
    tri.SetInput(sModel.GetPolyData())

    elev = vtk.vtkElevationFilter()
    elev.SetInputConnection(tri.GetOutputPort())

    implicitDataSet = vtk.vtkImplicitDataSet()
    implicitDataSet.SetDataSet(elev.GetOutput())
    
    triangle = vtk.vtkTriangleFilter()
    triangle.SetInput(inputModel.GetPolyData())
    triangle.Update()

    computeNormals = vtk.vtkPolyDataNormals()
    computeNormals.SetInput(triangle.GetOutput())
    computeNormals.ComputeCellNormalsOn()
    computeNormals.Update()

    clip = vtk.vtkClipPolyData()
    clip.SetInput(computeNormals.GetOutput())
    clip.SetClipFunction(implicitDataSet)
    clip.InsideOutOff()
    clip.Update()

    clean = vtk.vtkCleanPolyData()
    clean.SetInput(clip.GetOutput())
    clean.Update()

    polydata = clean.GetOutput()

    cellData = polydata.GetCellData()
    normals = cellData.GetNormals()

    meanNormal = [0,0,0]
    nOfTuples = normals.GetNumberOfTuples()

    for cellIndex in range(0, nOfTuples):
      cellNormal = [0,0,0]
      cell = polydata.GetCell(cellIndex)
      
      normals.GetTuple(cellIndex, cellNormal)
      meanNormal[0] = meanNormal[0] + cellNormal[0]
      meanNormal[1] = meanNormal[1] + cellNormal[1]
      meanNormal[2] = meanNormal[2] + cellNormal[2]
        
    meanNormal[0] = meanNormal[0] / nOfTuples
    meanNormal[1] = meanNormal[1] / nOfTuples
    meanNormal[2] = meanNormal[2] / nOfTuples

    print("Normal: " + str(meanNormal))

    seed1 = [0,0,0]
    seedList.GetNthFiducialPosition(0,seed1)
    vector = [seed1[0]+50*meanNormal[0],
              seed1[1]+50*meanNormal[1],
              seed1[2]+50*meanNormal[2]]
    seedList.AddFiducialFromArray(vector)

    # Calculate perpendicular vectors
    v1 = [0,0,0]
    v2 = [0,0,0]

    math = vtk.vtkMath()
    math.Perpendiculars(meanNormal, v2, v1, 0)

    # Normalize vectors
    math.Normalize(meanNormal)
    math.Normalize(v1)
    math.Normalize(v2)

    # create matrix4x4
    transform = slicer.mrmlScene.CreateNodeByClass('vtkMRMLLinearTransformNode') 
    slicer.mrmlScene.AddNode(transform)
    matrix = transform.GetMatrixTransformToParent()
    
    matrix.SetElement(0,0,v1[0])
    matrix.SetElement(1,0,v1[1])
    matrix.SetElement(2,0,v1[2])
    matrix.SetElement(3,0,0.0)

    matrix.SetElement(0,1,meanNormal[0])
    matrix.SetElement(1,1,meanNormal[1])
    matrix.SetElement(2,1,meanNormal[2])
    matrix.SetElement(3,1,0.0)

    matrix.SetElement(0,2,v2[0])
    matrix.SetElement(1,2,v2[1])
    matrix.SetElement(2,2,v2[2])
    matrix.SetElement(3,2,0.0)

    matrix.SetElement(0,3,seed1[0])
    matrix.SetElement(1,3,seed1[1])
    matrix.SetElement(2,3,seed1[2])
    matrix.SetElement(3,3,1.0)


    return True


class TestRobotPlacementTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TestRobotPlacement1()

  def test_TestRobotPlacement1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TestRobotPlacementLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
