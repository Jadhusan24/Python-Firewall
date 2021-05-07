import os
import csv


def compare_rules(primary_rule: str, secondary_rules: list):
    result = []
    for rule in secondary_rules:
        if str(primary_rule).strip() == str(rule).strip():
            result.append(True)
        else:
            result.append(False)

    return any(result)


def validate_with_route_table(src_addr, dst_addr, src_port, dst_port):
    try:
        rules_stream = open("./imports/Rules.csv", "r")
        rules = csv.reader(rules_stream)

        for rule in rules:
            # check for IP
            if compare_rules(rule[0], [src_addr, "any"]) and compare_rules(rule[2], [dst_addr, "any"]):
                # check for port
                if compare_rules(rule[1], [src_port, "any", 0]) and compare_rules(rule[3], [dst_port, "any", 0]):
                    return True
        return False
    except Exception as e:
        print(f"[ERR] Error reading rules: {e}")
        return False


# print(validate_with_route_table("0.0.0.0", "127.0.0.0", 22, 22))
# print(validate_with_route_table("192.168.2.100", "192.168.1.100", 22, 0))
# print(validate_with_route_table("192.168.2.100", "100", 80, 90))
