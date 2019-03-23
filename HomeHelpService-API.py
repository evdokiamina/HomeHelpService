import kivy
kivy.require('1.0.1') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout

Builder.load_file("styling.kv")

class LoginScreen(Screen):
  # def __init__(self, **kwargs):
  #     super(LoginScreen, self).__init__(**kwargs)
  #     # self.cols = 2
  #     self.add_widget(Label(text='User Name'))
      # self.username = TextInput(multiline=False)
      # self.add_widget(self.username)
  #     # self.add_widget(Label(text='password'))
  #     # self.password = TextInput(password=True, multiline=False)
  #     # self.add_widget(self.password)
  pass

class DataScreen(Screen):
  pass

class MainScreen(Screen):
  pass

sm = ScreenManager(transition=FadeTransition())
sm.add_widget(LoginScreen(name='login'))
sm.add_widget(MainScreen(name='main'))
sm.add_widget(DataScreen(name='data'))

class MyApp(App):
  def build(self):
    return sm
  
if __name__ == '__main__':
  MyApp().run() 