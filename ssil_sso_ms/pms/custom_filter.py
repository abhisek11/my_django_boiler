def custom_filter(self,model_name='',filter_columns=dict(),
                  fetch_columns=list(),fetch_obj=list(),single_row=False):
    # print('model_name',model_name)
    # print('filter_columns',filter_columns)
    # print('fetch_columns1',fetch_columns)
    if fetch_columns:
        if single_row:
            res = model_name.objects.filter(**filter_columns).values(*fetch_columns)
            if res:
                return model_name.objects.filter(**filter_columns).values(*fetch_columns)[0]
            else:
                return dict()
        else:
            return model_name.objects.filter(**filter_columns).values(*fetch_columns)
    else:
        if single_row:
            res = model_name.objects.filter(**filter_columns)
            if res:
                return model_name.objects.filter(**filter_columns)[0]
            else:
                return dict()
        else:
            return model_name.objects.filter(**filter_columns)