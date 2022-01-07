import functools
import numpy as np

import matplotlib.axes

from .projections import PlateCarree

__all__ = ["SkyAxes"]


def _add_lonlat(func):
    """Decorator to add lonlat option."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if kwargs.pop('lonlat', True):
            kwargs['transform'] = self.projection
        return func(self, *args, **kwargs)
    return wrapper


class SkyAxes(matplotlib.axes.Axes):
    def __init__(self, *args, **kwargs):
        self.projection = kwargs.pop("sky_projection")

        self.plate_carree = PlateCarree()

        super().__init__(*args, **kwargs)

    def cla(self):
        """Clear the current axes."""
        result = super().cla()
        self.xaxis.set_visible(False)
        self.yaxis.set_visible(False)

        # Whether the frame should be on is a decision of the axis artist maybe?
        self.set_frame_on(False)

        # Always equal aspect ratio.
        self.set_aspect('equal')

        # Can set datalim here based on projection?  Though
        # that I think is unnecessary because I redo everything anyway.

        return result

    def set_extent(self, extent, lonlat=True):
        """Set the extent of the axes.

        Parameters
        ----------
        extent : `tuple` [`float`]
            Set the extent by [lon0, lon1, lat0, lat1] or [x0, x1, y0, y1].
        lonat : `bool`, optional
            Extent is specified in lon/lat coordinates?  Otherwise native.
        """
        if not lonlat:
            x0, x1, y0, y1 = extent
        else:
            # Need to do transformation.
            lon0, lon1, lat0, lat1 = extent

            # Check if the longitude range is the full sphere, and special case that.
            if np.isclose(np.abs(lon1 - lon0), 360.0):
                lat_steps = [lat0, lat1]
                if lat0 < 0.0 and lat1 > 0.0:
                    # Make sure we have the equator included
                    lat_steps.append(0.0)
                lon, lat = np.meshgrid(np.linspace(0, 360.0, 360), lat_steps)
                xy = self.projection.transform_points(self.plate_carree, lon.ravel(), lat.ravel())
                # Need to offset this by some small amount to ensure we don't get
                # out-of-bounds transformations.
                eps = 1e-5
                x0 = (1 - eps)*np.min(xy[:, 0])
                x1 = (1 - eps)*np.max(xy[:, 0])
                y0 = (1 - eps)*np.min(xy[:, 1])
                y1 = (1 - eps)*np.max(xy[:, 1])
            else:
                # Make a ring of points and check their extent.
                npt = 100
                lon_pts = np.linspace(lon0, lon1, npt)
                lat_pts = np.linspace(lat0, lat1, npt)
                lon = np.concatenate((lon_pts, lon_pts, np.repeat(lon0, npt), np.repeat(lon1, npt)))
                lat = np.concatenate((np.repeat(lat0, npt), np.repeat(lat1, npt), lat_pts, lat_pts))
                xy = self.projection.transform_points(self.plate_carree, lon, lat)
                # NOTE NEED TO KNOW LON_0/WRAP OF PROJECTION...
                x0 = np.min(xy[:, 0])
                x1 = np.max(xy[:, 0])
                y0 = np.min(xy[:, 1])
                y1 = np.max(xy[:, 1])

        self.set_xlim([x0, x1])
        self.set_ylim([y0, y1])

    def get_extent(self, lonlat=True):
        """Get the extent of the axes.

        Parameters
        ----------
        lonlat : `bool`, optional
            Return extent in lon/lat coordinates?  Otherwise native.
        """
        x0, x1 = self.get_xlim()
        y0, y1 = self.get_ylim()

        if not lonlat:
            extent = (x0, x1, y0, y1)
        else:
            # Make a ring of points and check their extent.
            npt = 100
            x_pts = np.linspace(x0, x1, npt)
            y_pts = np.linspace(y0, y1, npt)
            x = np.concatenate((x_pts, x_pts, np.repeat(x0, npt), np.repeat(x1, npt)))
            y = np.concatenate((np.repeat(y0, npt), np.repeat(y1, npt), y_pts, y_pts))
            lonlat = self.plate_carree.transform_points(self.projection, x, y)

            # Check for out-of-bounds by reverse-projecting
            xy = self.projection.transform_points(self.plate_carree, lonlat[:, 0], lonlat[:, 1])
            bad = ((~np.isclose(xy[:, 0], x)) | (~np.isclose(xy[:, 1], y)))
            lonlat[bad, :] = np.nan

            lon0 = np.nanmin(lonlat[:, 0])
            lon1 = np.nanmax(lonlat[:, 0])
            lat0 = np.nanmin(lonlat[:, 1])
            lat1 = np.nanmax(lonlat[:, 1])

            if self.xaxis_inverted():
                extent = (lon1, lon0, lat0, lat1)
            else:
                extent = (lon0, lon1, lat0, lat1)

        return extent

    @_add_lonlat
    def plot(self, *args, **kwargs):
        # Line segments that cross should be split.  I think the
        # path code might do this?
        # In fact it will always do geodesic curves?  That would be cool.
        result = super().plot(*args, **kwargs)

        return result

    @_add_lonlat
    def scatter(self, *args, **kwargs):
        result = super().scatter(*args, **kwargs)

        return result

    @_add_lonlat
    def pcolormesh(self, *args, **kwargs):
        # This is going to take much more work.
        result = super().pcolormesh(*args, **kwargs)

        return result

    @_add_lonlat
    def fill(self, *args, **kwargs):
        # This might be more work?
        result = super().fill(*args, **kwargs)

        return result
