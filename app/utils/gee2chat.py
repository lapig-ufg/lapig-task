
def group_to_dataset(data):
    groups = data['groups']
    result = []

    for class_id in [1,2,3]:
        try:
            value = None
            filter_data = list(filter(lambda x: x['class'] == class_id, groups))[0]
            for i in ['mean', 'sum']:
                if i in filter_data.keys():
                    value =  filter_data[i]
        except:
            pass
        result.append((class_id,value))
    
    return result

def get_chat_pasture(pasture_data):
    datasets = {}
    for obj in pasture_data:
        properties =obj['properties']
        index = properties['indexs']
        for index_name in ['area_ha','CAI','NDVI','NWDI','precipitation']:
            if not properties.get(index_name,None) is None:
                info = properties[index_name]
            else:
                info = index[index_name]
            try:
                datasets[index_name.lower()]['label'].append(properties['year'])
                datasets[index_name.lower()]['datasets'][0]['data'].append(info)
            except:
                datasets[index_name.lower()] = {
                    'label':[properties['year']],
                    'datasets':[{
                        'label': index_name.lower(),
                        'data':[info]
                    }]
                }

    return datasets

def get_chat_pasture_vigor(pasture_data):
    datasets = {}
    years = []
    for obj in pasture_data:
        properties =obj['properties']

        for index_name in obj['properties']:
            if index_name == 'year':
                years.append(properties['year'])
            else:
                info = properties[index_name]
                try:
                    datasets[index_name.lower()]['label'] = years
                    for i, valeu in enumerate(group_to_dataset(info)):
                        datasets[index_name.lower()]['datasets'][i]['label'] = f"class_{valeu[0]}"
                        datasets[index_name.lower()]['datasets'][i]['data'].append(valeu[1])
                except:
                    values = []
                    for i, valeu in enumerate(group_to_dataset(info)):
                        values.append({
                            'label': f"class_{valeu[0]}",
                            'data':[valeu[1]]
                        })
                    datasets[index_name.lower()] = {
                        'label':years,
                        'datasets':values
                    }

    return datasets