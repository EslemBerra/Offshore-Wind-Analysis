def hesapla_capex(kapasite_mw, derinlik, mesafe):
    foundation_cost = derinlik * 100000
    grid_cost = mesafe * 50000
    turbine_cost = kapasite_mw * 1200000
    return turbine_cost + foundation_cost + grid_cost

def hesapla_opex(kapasite_mw):
    return kapasite_mw * 70000  # yıllık

def hesapla_aep(kapasite_mw, kapasite_faktoru):
    return kapasite_mw * kapasite_faktoru * 8760

def hesapla_lcoe(capex, opex, aep, oran=0.08, omur=25):
    crf = (oran * (1 + oran) ** omur) / ((1 + oran) ** omur - 1)
    return (capex * crf + opex) / aep




