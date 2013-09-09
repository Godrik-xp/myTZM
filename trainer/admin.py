from django.contrib import admin
from TZM.trainer.models import *

admin.site.register(Photo)

admin.site.register(RECategory)
#admin.site.register(REState)
admin.site.register(RELog)

admin.site.register(RETestQuestion)
admin.site.register(RETestAnswer)

#admin.site.register(RESyncBlock)

admin.site.register(RESyncState)
admin.site.register(RESync)

"""
admin.site.register(Ochenka)
admin.site.register(Uchebnaya_Zadacha)
admin.site.register(Otsenka_po_kvu_oshibok)
admin.site.register(Urov_slogh)
admin.site.register(Vozm_ochibka)
admin.site.register(Vipoln_uch_zad)
admin.site.register(Ochibka_vipoln_zad)
admin.site.register(Otcenka_po_vrem_vip)
"""