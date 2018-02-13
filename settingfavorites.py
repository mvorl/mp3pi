#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Das Modul lädt Stationslisten (entweder von radio.de oder aus
custom.json) zur Auswahl der Favoriten.
"""

import re
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.listview import ListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.settings import SettingItem

from radiostations import RadioStations

# import pdb
# import pprint


settingFavorites = None

class FavListListView(ListView):

  def scroll_to(self, index=0):
    if not self.scrolling:
      self.scrolling = True
      self._index = index

      #self.populate()
      mstart = index * self.row_height
      scroll_y = mstart / (self.container.height - self.height)
      scroll_y = 1 - min(1, max(scroll_y, 0))
      scrlv = self.container.parent
      scrlv.scroll_y = scroll_y
      scrlv._update_effect_y_bounds() # bug in ScrollView

      self.dispatch('on_scroll_complete')


class FavoritesBox(BoxLayout):

  stations = None

  favListStart = None
  favListNow = None

  # References to kv widgets
  favListStationsList = ObjectProperty(None)
  favListStationsSlider = ObjectProperty(None)
  favListFilterInput = ObjectProperty(None)
  favListSaveButton = ObjectProperty(None)
  favListCancelButton = ObjectProperty(None)

  def args_converter(self, row_index, an_obj):
    """Argument-Konverter für den ListAdapter des ListView der Stationsliste.
    
    Eingabe ist der Zeilenindex row_index des zu konstruierenden
    ListView-Elements und das Datenobjekt an_obj. Es enthält
    das Dictionary mit Stationsdaten, wie es von der Klasse
    Radiostations generiert wird.

    Rückgabewert ist ein Dictionary, das zur Konstruktion des
    ListItemButtonTitle verwendet wird.
    """
    if row_index % 2:
      background = [1, 1, 1, 0]
    else:
      background = [1, 1, 1, .5]

    return {'text': an_obj['name'],
            'is_selected': an_obj['is_selected'],
            'deselected_color': background,
    }

  def __init__(self, **kwargs):
    super(FavoritesBox, self).__init__(**kwargs)

    self.stations = RadioStations()

    playlist = App.get_running_app().config.get('General', 'playlist')
    # Select the corresponding toggle button
    pltb = ToggleButtonBehavior.get_widgets('playlist')
    for tb in pltb:
        tb.state = 'down' if tb.text == playlist else 'normal'
    del pltb
    self.change_playlist(playlist)

    self.favListStart = set()
    self.favListNow = set()
    for station in self.stations.favorites:
      self.favListStart.add(station['name'])
      self.favListNow.add(station['name'])

    self.favListStationsList.adapter.bind(on_selection_change=self.change_selection)

    # Set up the draggable scrollbar  
    scrlv = self.favListStationsList.container.parent # The ListView's ScrollView
    scrls = self.favListStationsSlider
    scrlv.bind(scroll_y=partial(self.scroll_slider,scrls))
    scrls.bind(value=partial(self.scroll_list,scrlv))

  def scroll_list(self, scrlv, scrls, value):
    """Scrollen der Stationsliste.
    
    Gebunden an die value-Property des Stationslisten-Sliders in __init__.
    """
    scrlv.scroll_y = value
    scrlv._update_effect_y_bounds() # bug in ScrollView
    
  def scroll_slider(self, scrls, scrlv, value):
    """Scrollen des Stationslisten-Sliders.
    
    Gebunden an die scroll_y-Property der Stationsliste in __init__.
    """
    if value >= 0:
      #this to avoid 'maximum recursion depth exceeded' error
      scrls.value = value

  def change_selection(self, adapter):
    """Wechsel der Startionsauswahl.
    
    Gebunden an die on_selection_change-Property von search_results_list in __init__
    """
    for item in adapter.data:
      if item['is_selected']:
        self.favListNow.add(item['name'])
      elif item['name'] in self.favListNow:
        self.favListNow.remove(item['name'])

  def getFilter(self):
    """Auslesen des Filter-Textfelds.
    
    Wildcards * und ? werden auf reguläre Ausdrücke umgesetzt.
    Ausnahme: das Muster beginnt mit ^. Dann wird es verbatim
    verwendet.
    """
    pattern = self.favListFilterInput.text
    if pattern[0] != '^':
      pattern = pattern.replace('*','.*')
      pattern = pattern.replace('?','.')
      if pattern[0] != '^':
        pattern = '^' + pattern
      if pattern[-1] != '$':
        pattern = pattern + '$'
      pattern = '(?i)' + pattern
    return re.compile(pattern)

  def update_list(self):
    """Aktualisieren der Stationsliste.
    
    on_text-Callback von favListFilterInput, s. mp3pi.kv
    """
    if not self.stations.no_data:
      filter = self.getFilter()
      data = []
      for station in self.stations.data:
        if filter.match(station['name']):
          data.append(station)
          del self.favListStationsList.adapter.data[:]
          self.favListStationsList.adapter.data.extend(data)

  def change_playlist(self, playlist):
    """Auswahl der Quelle der Stationsliste.
    
    on_release-Callback der Stationsliste-Auswahl-Buttons; s. mp3pi.kv
    """
    self.stations.load_playlist(playlist)
    if not self.stations.no_data:
      for station in self.stations.data:
        station['is_selected'] = self.stations.getListItemByName(self.stations.favorites, station['name']) is not None
    self.update_list()

  def saveFavlist(self):
    """Speichern der Favoriten und Beenden der Bearbeitung.
    
    on_release-Callback des Save-Buttons; s. mp3pi.kv
    """
    global settingFavorites
    for item in self.favListNow - self.favListStart:
      Logger.info('Favorites: add '+item)
      self.stations.addToFavorites(item)
    for item in self.favListStart - self.favListNow:
      Logger.info('Favorites: remove '+item)
      self.stations.removeFromFavorites(item)
    settingFavorites.close(reload=True)

  def cancelFavlist(self):
    """Abbruch der Bearbeitung.
    
    on_release-Callback des Cancel-Buttons; s. mp3pi.kv
    """
    global settingFavorites
    settingFavorites.close()


class SettingFavorites(SettingItem):
  """Klasse zum Bearbeiten der Favoriten als Einstellung."""
  
  popup = ObjectProperty(None)
  '''(internal) Used to store the current popup when it is shown.
  
  :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
  to None.
  '''

  def __init__(self, **kwargs):
    super(SettingFavorites, self).__init__(**kwargs)
    self.value = BooleanProperty(False)

  def on_panel(self, instance, value):
    global settingFavorites
    if value is None:
      return
    self.fbind('on_release', self._create_popup)
    settingFavorites = self

  def _create_popup(self, instance):
    content = FavoritesBox()
    self.popup = Popup(title=self.title, content=content,
                  size_hint=(None, 0.9), width=0.95*Window.width)
    self.popup.open()

  def close(self, reload=False):
    if self.popup:
      self.popup.dismiss()
    if reload:
      # Force a value change
      self.value = not self.value
