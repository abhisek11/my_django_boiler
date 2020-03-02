from django.db import transaction, IntegrityError
def custom_delete(self,instance, validated_data,update_extra_columns=list(),
                  extra_model_with_fields=list()):
    try:
        with transaction.atomic():
            instance.is_deleted = True
            instance.updated_by = validated_data.get('updated_by')
            if update_extra_columns:
                for e_udate_c in update_extra_columns:
                    instance.__dict__[e_udate_c] = False
            instance.save()
            #print('dsfsdfdff')
            for e_extra_model_with_fields in  extra_model_with_fields:
                #print('e_extra_model_with_fields', e_extra_model_with_fields)
                extra_model_d = e_extra_model_with_fields['model'].objects.filter(
                    **e_extra_model_with_fields['filter_columns'])
                #print('extra_model_d',extra_model_d)
                if extra_model_d:
                    for e_extra_model_d in extra_model_d:
                        #print('extra_model_d',extra_model_d)
                        e_extra_model_d.is_deleted = True
                        e_extra_model_d.updated_by = validated_data.get('updated_by')
                        if e_extra_model_with_fields['update_extra_columns']:
                            for u_update_c in e_extra_model_with_fields['update_extra_columns']:
                                e_extra_model_d.__dict__[u_update_c] = False
                        e_extra_model_d.save()
            return instance
    except Exception as e:
        raise e