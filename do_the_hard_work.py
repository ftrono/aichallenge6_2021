from utils import mongo_connect, get_data_from_db, filter_series, clipping, plot_series, normalize

db,client = mongo_connect()
POSTS = db.test2

i = 0
for riduttore in POSTS.find():
    if i == 10:
        break
    for pressata in riduttore['steps']:
        if i == 10:
            break

        id = get_data_from_db(pressata, 'id')
        altezza = get_data_from_db(pressata, 'altezza')
        forza = get_data_from_db(pressata, 'forza')
        plot = plot_series(id, altezza, forza, title='Original')
        print(plot)

        # Filtering hi-frequencies
        hi_pass_forza, hi_pass_altezza = clipping(forza, altezza)
        # Filtering lo-frequencies
        filtered_altezza = filter_series(hi_pass_altezza)
        filtered_forza = filter_series(hi_pass_forza)


        # Saving changes...
        pressata['altezza'] = filtered_altezza
        pressata['forza'] = filtered_forza

        # Normalize array
        normalized_array = normalize(pressata)
        plot = plot_series(normalized_array['id'], normalized_array['altezza'], normalized_array['forza'], title='Norm+Filter')
        print(plot)

        print(f'id: {id}\n'
              f'forza: {normalized_array["forza"]}\n'
              f'altezza: {normalized_array["altezza"]}')
        i += 1