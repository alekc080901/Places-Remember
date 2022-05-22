from folium import LatLngPopup, ClickForMarker
from jinja2 import Template


class EditedLatLngPopup(LatLngPopup):

    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Latitude: " + e.latlng.lat.toFixed(8) +
                                    "<br>Longitude: " + e.latlng.lng.toFixed(8))
                        .openOn({{this._parent.get_name()}});
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super().__init__()


class EditedClickForMarker(ClickForMarker):
    _template = Template(u"""
                {% macro script(this, kwargs) %}
                    function newMarker(e){
                        var new_mark = L.marker(e.latlng, {icon: L.AwesomeMarkers.icon({icon: 'heart', markerColor: 'red'})}).addTo({{this._parent.get_name()}});
                        new_mark;
                        new_mark.on('dblclick', function(e){ {{this._parent.get_name()}}.removeLayer(e.target)})
                        var lat = e.latlng.lat.toFixed(4),
                           lng = e.latlng.lng.toFixed(4);
                        new_mark.bindPopup({{ this.popup }});
                        };
                    {{this._parent.get_name()}}.on('click', newMarker);
                {% endmacro %}
                """)

    def __init__(self):
        super().__init__()
