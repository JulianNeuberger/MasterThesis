from django.http import HttpResponse

from data.processing import run_pre_processing


def pre_process_data_view(request):
    run_pre_processing()
    return HttpResponse('Finished pre processing data, see logs for more information')
