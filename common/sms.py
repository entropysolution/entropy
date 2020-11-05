import nexmo
import plivo
import smpplib
import logging

log = logging.getLogger('common.sms')

def sendit_nexmo(mobile_number, sender, message, provider):
    nexmo_api_key = provider.get('key')
    nexmo_api_secret = provider.get('secret')
    if nexmo_api_key is None or nexmo_api_secret is None:
        log.warning('Trying to send SMS using Nexmo with incomplete configuration.')
        return False
    client = nexmo.Client(key=nexmo_api_key, secret=nexmo_api_secret)
    client.send_message({
        'from': sender,
        'to': mobile_number,
        'text': message,
    })
    return True


def sendit_plivo(mobile_number, sender, message, provider):
    plivo_auth_id = provider.get('id')
    plivo_auth_token = provider.get('token')
    if plivo_auth_id is None or plivo_auth_token is None:
        log.warning('Trying to send SMS using Plivo with incomplete configuration.')
        return False
    client = plivo.RestClient(auth_id=plivo_auth_id, auth_token=plivo_auth_token)
    client.messages.create(
        src = sender,
        dst = mobile_number,
        text = message
    )
    return True


def sendit_smsc(mobile_number, sender, message, provider):
    smsc_hostname = provider.get('hostname')
    smsc_port = provider.get('port')
    smsc_system_id = provider.get('system_id')
    smsc_password = provider.get('system_password') 
    smsc_system_type = provider.get('system_type')
    if smsc_hostname is None or smsc_port is None or smsc_system_id is None or smsc_password is None or smsc_system_type is None:
        log.warning('Trying to send SMS using SMSC with incomplete configuration.')
        return False
    client = smpplib.client.Client(smsc_hostname, smsc_port)
    client.connect()
    client.bind_transmitter(system_id=smsc_system_id, password=smsc_password, system_type=smsc_system_type)
    length = len(message)
    splitat = 160
    parts = length/splitat+1
    if length > splitat:
        for k in range(parts):
            msgpart = message[k*splitat:k*splitat+splitat]
            client.send_message(
                source_addr_ton=smpplib.command.SMPP_TON_ALNUM,
                source_addr_npi = 5,
                source_addr=sender,
                dest_addr_ton=smpplib.command.SMPP_TON_UNK,
                dest_addr_npi = smpplib.command.SMPP_NPI_ISDN,
                destination_addr=mobile_number,
                sar_msg_ref_num = 1,
                sar_total_segments = parts,
                sar_segment_seqnum = k+1,
                message_payload=msgpart)
    else:
        client.send_message(
            source_addr_ton=smpplib.command.SMPP_TON_ALNUM,
            source_addr_npi = 5,
            source_addr=sender,
            dest_addr_ton=smpplib.command.SMPP_TON_UNK,
            dest_addr_npi = smpplib.command.SMPP_NPI_ISDN,
            data_coding=smpplib.command.SMPP_ENCODING_ISO88591,
            destination_addr=mobile_number,
            short_message=message)
    client.unbind()    
    client.disconnect()
    return True