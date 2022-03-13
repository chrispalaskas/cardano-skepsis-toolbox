from pickle import TRUE
import helper
import json
from os.path import exists


def main(poolID: str, delegatorsLogFile: str, blockFrostURL: str, blockFrostProjID: str):

    current_epoch = helper.getCurrentEpoch(blockFrostURL, blockFrostProjID)
    if not exists(delegatorsLogFile):
        f = open(delegatorsLogFile, "w")
        f.write("{}")
        f.close()

    with open(delegatorsLogFile, 'r') as jsonlog:
        delegators_dict = json.load(jsonlog)
        new_delegators_dict = {}
        epoch_list = list(delegators_dict.keys())
        epoch_list.sort(reverse=True)
        if current_epoch != 0:
            # current_epoch_dict = helper.getDelegatorsBlockfrost(poolID, blockFrostURL, blockFrostProjID)
            current_epoch_dict = helper.getDelegatorsKoios(poolID, koiosURL, current_epoch)
        if len(epoch_list) >= 2 and current_epoch == int(epoch_list[1]):
            print("Already added current epoch's delegations")
            return 0
        if 'sum' in epoch_list:
            old_delegation_sum_dict = delegators_dict['sum'].copy()
            new_delegators_dict['sum'] = {
                k: current_epoch_dict.get(k, 0) + old_delegation_sum_dict.get(k, 0) \
                    for k in set(current_epoch_dict) | set(old_delegation_sum_dict)}
        else:
            new_delegators_dict['sum'] = current_epoch_dict
        new_delegators_dict[str(current_epoch)] = current_epoch_dict
        with open(delegatorsLogFile, 'w') as jsonlog:
            json.dump(new_delegators_dict, jsonlog, indent=4, sort_keys=False)


if __name__ == '__main__':
    print('Get a list of delegators and their ')
    configFile = './config.json'
    delegatorsLogFile, \
    blockFrostURL, \
    blockFrostProjID, \
    koiosURL, \
    poolID = helper.parseConfigGetDelegators(configFile)

    main(poolID, delegatorsLogFile, blockFrostURL, blockFrostProjID )