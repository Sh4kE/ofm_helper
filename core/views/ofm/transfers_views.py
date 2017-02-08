import numpy
from braces.views import CsrfExemptMixin
from braces.views import JsonRequestResponseMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from core.managers.panda_manager import PandaManager


@method_decorator(login_required, name='dispatch')
class TransfersChartView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def get(self, request):
        group_by = request.GET.get('group_by', default='Strength')

        ages = self._to_int_list(request.GET.get('ages', default=None))
        strengths = self._to_int_list(request.GET.get('strengths', default=None))
        positions = self._to_list(request.GET.get('positions', default=None))
        seasons = self._to_int_list(request.GET.get('seasons', default=None))
        matchdays = self._to_int_list(request.GET.get('matchdays', default=None))
        min_price = self._to_int(request.GET.get('min_price', default=None))
        max_price = self._to_int(request.GET.get('max_price', default=None))

        if positions == 'All':
            positions = None

        panda_manager = PandaManager()
        prices = panda_manager.get_grouped_prices(group_by,
                                                  ages=ages,
                                                  strengths=strengths,
                                                  positions=positions,
                                                  seasons=seasons,
                                                  matchdays=matchdays,
                                                  min_price=min_price,
                                                  max_price=max_price,
                                                  )

        chart_json = {
            "series": [
                {
                    "name": 'Preise',
                    "data": self._get_data_from_dataframe(prices)
                },
            ],
            "categories":
                list(map(int, numpy.array(prices.mean().index)))
        }

        return self.render_json_response(chart_json)

    @staticmethod
    def _get_data_from_dataframe(prices):
        mins = prices.min()
        quantiles = prices.quantile([0.25, 0.75])
        medians = prices.median()
        maxs = prices.max()
        data = []
        for x_index in numpy.array(prices.mean().index):
            data.append([float(mins[x_index]),
                         float(quantiles[x_index][0.25]),
                         float(medians[x_index]),
                         float(quantiles[x_index][0.75]),
                         float(maxs[x_index])
                         ])
        return data

    @staticmethod
    def _to_int_list(l):
        if l:
            return list(map(int, l.split(',')))
        return None

    @staticmethod
    def _to_list(l):
        if l:
            return l.split(',')
        return None

    @staticmethod
    def _to_int(l):
        if l:
            return int(l)
        return None


@method_decorator(login_required, name='dispatch')
class TransfersView(TemplateView):
    template_name = 'core/ofm/transfers.html'