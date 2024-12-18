"""Configures KSQL to combine station and turnstile data"""
import json
import logging

import requests

import topic_check


logger = logging.getLogger(__name__)


KSQL_URL = "http://localhost:8088"

#
# TODO: Complete the following KSQL statements.'
# TODO: For the first statement, create a `turnstile` table from your turnstile topic.
#       Make sure to use 'avro' datatype!
# TODO: For the second statment, create a `turnstile_summary` table by selecting from the
#       `turnstile` table and grouping on station_id.
#       Make sure to cast the COUNT of station id to `count`
#       Make sure to set the value format to JSON

KSQL_STATEMENT = """
CREATE TABLE turnstiles (
  station_id INT,
  station_name VARCHAR,
  line VARCHAR
) WITH (
  KAFKA_TOPIC='org.chicago.cta.station.turnstiles',
  VALUE_FORMAT='AVRO',
  KEY='station_id'
);

CREATE TABLE turnstile_summary
WITH (VALUE_FORMAT='JSON') AS
SELECT
  station_id, COUNT(*) AS count
FROM turnstiles
GROUP BY station_id;
"""


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    if topic_check.topic_exists("turnstile_summary") is True:
        return

    logging.debug("executing ksql statement...")

    resp = requests.post(
        f"{KSQL_URL}/ksql",
        headers={"Content-Type": "application/vnd.ksql.v1+json"},
        data=json.dumps(
            {
                "ksql": KSQL_STATEMENT,
                "streamsProperties": {"ksql.streams.auto.offset.reset": "earliest"},
            }
        ),
    )

    # Ensure that a 2XX status code was returned
    try:
      resp.raise_for_status()
    except:
      print(f"failed creating KSQL request: {json.dumps(resp.json(), indent=2)}")
      exit(1)

if __name__ == "__main__":
    execute_statement()
