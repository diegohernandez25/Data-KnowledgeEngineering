from django.shortcuts import render

# Create your views here.


def index(request):
    tparams = {}
    info = "Airport details"
    # (src_lat, src_long, dst_lat, dst_long)
    tparams['route'] = [(1, -6.081689, 145.391881, 1, "Airport 1", info, 32.896828, -97.037997, 2, "Airport 2", info),
                        (2, 76.531203, -68.703161, 3, "Airport 3", info, -18.095881, 25.839006, 4, "Airport 4", info),
                        (3, -4.481689, 125.391881, 5, "Airport 5", info, 47.896828, -37.037997, 6, "Airport 6", info),
                        (4, 53.531203, 54.703161, 7, "Airport 7", info, -10.095881, 12.839006, 8, "Airport 8", info)]

    return render(request, 'index.html',tparams)
