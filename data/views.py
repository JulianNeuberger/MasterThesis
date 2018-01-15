from django.http import HttpResponse

from data.processing import get_raw, pre_process, dump_pre_processed


def pre_process_data_view(request):
    xs, ys = get_raw()
    processed = pre_process(xs, ys)
    dump_pre_processed(processed)
    return HttpResponse('Finished pre processing data, see logs for more information')
