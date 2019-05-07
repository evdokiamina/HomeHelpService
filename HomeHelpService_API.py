import kivy
kivy.require('1.0.1') # replace with your current kivy version !

import HomeHelpService_Database as DB
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.uix.treeview import TreeView, TreeViewLabel
# from kivy.uix.treeview.TreeViewLabel import TreeViewLabel 
from kivy.properties import ObjectProperty, ListProperty
from kivy.garden.mapview import MapView, MapMarker, MarkerMapLayer

class AssignmentsList(BoxLayout):
  assignments_list = ObjectProperty(None)
  # print(tour)

  def __init__(self, **kwargs):
    super(AssignmentsList, self).__init__(**kwargs)
    l = Label(text='ASSIGNMENT LIST')
    tv = TreeView(root_options=dict(text='Assignments'), hide_root=True)
    for t in tour:
      for node in t:
        if node in E: 
          itemNameTemp = str(data[node][1]) + ' ' + str(data[node][2])
          branchNameTemp = tv.add_node(TreeViewLabel(text =itemNameTemp,  is_open=True))
      for node in t:
        if node not in E:
          dropItem = str(data[node][1]) + ' ' + str(data[node][2])
          tv.add_node(TreeViewLabel(text=dropItem), branchNameTemp)
    # self.add_widget(l)
    self.add_widget(tv)
    tv.bind(on_node_expand=lambda self,evt:ViewMap().nodeExpanded())
    tv.bind(on_node_collapse=lambda self,evt:ViewMap().nodeColapsed())

class ViewMap(BoxLayout):

  def __init__(self, **kwargs):
    super(ViewMap, self).__init__(**kwargs)
    self.build()

  def build(self):
    self.mapview = MapView(lat=51.48, lon=-3.17, zoom=11)
    self.mapLayer = MarkerMapLayer()
    for i in locations:
      locationLat = float(locations[i][0])
      locationLon =  float(locations[i][1])
      marker = MapMarker(lat=locationLat, lon=locationLon)
      self.mapLayer.add_widget(marker)
    self.mapview.add_layer(self.mapLayer)
    self.add_widget(self.mapview)

  def update(self):
    print('updating map')

  def nodeExpanded(self):
    print('expanded node')

  def nodeColapsed(self):
    print('node colapsed')


class DataScreen(Screen):

  def __init__(self, **kwargs):
    super(DataScreen, self).__init__(**kwargs)
  pass

class MyApp(App):
  def build(self):
    return DataScreen()
  
if __name__ == '__main__':
  DB = DB.useDatabase
  E, N, locations, data = DB.getDBData()
  tour,e,n,relax = DB.runAlgorithm(N, E, locations)
  MyApp().run() 