def parse_amount(text):
    """Extract amount from text"""
    cleaned = text.replace(',', '').replace('RWF', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


def extract_between(text, start, end):
    """Extract text between two markers."""
    try:
        start_index = text.find(start)
        if start_index == -1:
            return None
        start_index += len(start)
        end_index = text.find(end, start_index)
        if end_index == -1:
            return None
        return text[start_index:end_index].strip()
    except:
        return None


def extract_name(text):
    """Clean up a name by removing extra whitespace."""
    if not text:
        return ''
    return ' '.join(text.split())


def extract_transaction_id(body):
    """Extract transaction ID from SMS body."""
    
    # Format: "TxId: 73214484437."
    if 'TxId: ' in body:
        transaction_id = extract_between(body, 'TxId: ', '.')
        if transaction_id and transaction_id.isdigit():
            return int(transaction_id)
    
    # Format: "*162*TxId:13913173274*S*"
    if '*TxId:' in body:
        transaction_id = extract_between(body, '*TxId:', '*')
        if transaction_id and transaction_id.isdigit():
            return int(transaction_id)
    
    # Format: "Financial Transaction Id: 76662021700."
    if 'Financial Transaction Id: ' in body:
        transaction_id = extract_between(body, 'Financial Transaction Id: ', '.')
        if transaction_id and transaction_id.isdigit():
            return int(transaction_id)
    
    # Format: "Transaction Id: 14098463509."
    if 'Transaction Id: ' in body:
        transaction_id = extract_between(body, 'Transaction Id: ', '.')
        if transaction_id and transaction_id.isdigit():
            return int(transaction_id)
    
    return None


def parse_sms_body(body):

    if 'one-time password' in body.lower():
        return None
    
    result = {
        'id': extract_transaction_id(body),
        'amount': 0,
        'type': 'unknown',
        'sender': '',
        'receiver': '',
        'created_at': ''
    }
    
    # Type 1: Received money
    if 'You have received' in body and 'RWF from' in body:
        amount_str = extract_between(body, 'received ', ' RWF')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        sender = extract_between(body, 'RWF from ', ' (')
        result['sender'] = extract_name(sender)
        result['receiver'] = 'Me'  # I am the receiver
        
        result['created_at'] = extract_between(body, ' at ', '. Message') or extract_between(body, ' at ', '. Your')
        result['type'] = 'received'
        return result
    
    # Type 2: Payment sent 
    if 'Your payment of' in body and 'has been completed' in body:
        if 'Airtime' in body or 'Cash Power' in body:
            pass  
        else:
            amount_str = extract_between(body, 'payment of ', ' RWF to')
            result['amount'] = parse_amount(amount_str) if amount_str else 0
            
            receiver_part = extract_between(body, 'RWF to ', ' has been completed')
            if receiver_part:
                parts = receiver_part.rsplit(' ', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    result['receiver'] = extract_name(parts[0])
                else:
                    result['receiver'] = extract_name(receiver_part)
            
            result['sender'] = 'Me'  # User is the sender
            result['created_at'] = extract_between(body, 'completed at ', '. Your')
            result['type'] = 'payment'
            return result
    
    # Type 3: Transfer sent
    if '*165*S*' in body and 'transferred to' in body:
        amount_str = extract_between(body, '*165*S*', ' RWF transferred')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        receiver = extract_between(body, 'transferred to ', ' (')
        result['receiver'] = extract_name(receiver)
        result['sender'] = 'Me'  # User is the sender
        
        result['created_at'] = extract_between(body, ') from ', ' . Fee')
        if result['created_at'] and ' at ' in result['created_at']:
            result['created_at'] = result['created_at'].split(' at ', 1)[1]
        
        result['type'] = 'transfer'
        return result
    
    # Type 4: Bank deposit
    if '*113*R*' in body and 'bank deposit' in body:
        amount_str = extract_between(body, 'deposit of ', ' RWF')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        result['created_at'] = extract_between(body, 'account at ', '. Your')
        result['sender'] = 'Bank Deposit'
        result['receiver'] = 'Me'  # User is the receiver
        result['type'] = 'deposit'
        return result
    
    # Type 5: Airtime purchase
    if '*162*' in body and 'Airtime' in body:
        amount_str = extract_between(body, 'payment of ', ' RWF to')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        result['created_at'] = extract_between(body, 'completed at ', '. Fee')
        result['sender'] = 'Me'  # User is the sender
        result['receiver'] = 'Airtime'
        result['type'] = 'airtime'
        return result
    
    # Type 6: Cash withdrawal
    if 'withdrawn' in body and 'via agent' in body:
        amount_str = extract_between(body, 'withdrawn ', ' RWF')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        agent = extract_between(body, 'via agent: ', ' (')
        result['receiver'] = extract_name(agent)
        result['sender'] = 'Me'  # User is the sender (withdrawing from user account)
        
        result['created_at'] = extract_between(body, 'account: ', ' at ')
        if not result['created_at']:
            result['created_at'] = extract_between(body, ') at ', ' and')
        
        result['type'] = 'withdrawal'
        return result
    
    # Type 7: Cash Power
    if '*162*' in body and 'Cash Power' in body:
        amount_str = extract_between(body, 'payment of ', ' RWF to')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        result['created_at'] = extract_between(body, 'completed at ', '. Fee')
        result['sender'] = 'Me'  # User is the sender
        result['receiver'] = 'MTN Cash Power'
        result['type'] = 'cash_power'
        return result
    
    # Type 8: Direct debit
    if '*164*S*' in body and 'transaction of' in body:
        amount_str = extract_between(body, 'transaction of ', ' RWF')
        result['amount'] = parse_amount(amount_str) if amount_str else 0
        
        receiver = extract_between(body, 'RWF by ', ' on your')
        result['receiver'] = extract_name(receiver)
        result['sender'] = 'Me'  # User is the sender (money debited from user account)
        
        result['created_at'] = extract_between(body, 'completed at ', '. Message')
        result['type'] = 'direct_debit'
        return result
    
    return None
