import time
import requests

class MetadataEnricher:
    """Enriches parsed metadata using external APIs like Discogs and MusicBrainz, preserving original data and provenance."""

    def __init__(self, config):
        self.config = config
        self.discogs_token = config.get("DISCOGS_TOKEN")
        self.musicbrainz_user_agent = config.get("MUSICBRAINZ_USER_AGENT", "RecordCatalogApp/1.0")

    def query_discogs(self, label, catalog_number, artist=None, title=None):
        if not label or not catalog_number:
            print("Discogs enrichment skipped: missing label or catalog number.")
            return {}
        headers = {"User-Agent": self.musicbrainz_user_agent}
        params = {
            "release_title": catalog_number,
            "per_page": 3,
            "page": 1,
            "token": self.discogs_token
        }
        # Add artist and title if provided
        if artist:
            params['artist'] = artist
        if title:
            params['title'] = title

        url = "https://api.discogs.com/database/search"
        print(f"Querying Discogs with label='{label}', catalog_number='{catalog_number}', artist='{artist}', title='{title}'")
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            if data.get('results'):
                print(f"Discogs returned {len(data['results'])} result(s)")
                return data['results']
            else:
                print("Discogs returned no results.")
        except Exception as e:
            print(f"Discogs API error: {e}")
        return {}

    def query_musicbrainz(self, title, artist):
        if not title or not artist:
            return {}
        url = "https://musicbrainz.org/ws/2/release/"
        params = {
            "query": f'release:{title} AND artist:{artist}',
            "fmt": "json",
            "limit": 1
        }
        headers = {"User-Agent": self.musicbrainz_user_agent}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            if 'releases' in data and data['releases']:
                release = data['releases'][0]
                return {
                    "Release Date": release.get('date'),
                    "Country": release.get('country'),
                }
        except Exception as e:
            print(f"MusicBrainz API error: {e}")
        return {}

    def enrich_metadata(self, metadata: dict) -> dict:
        label = metadata.get('Label')
        catalog_number = metadata.get('Catalog Number')
        artist = metadata.get('Artist')
        title = metadata.get('Title')
        discogs_results = self.query_discogs(label, catalog_number, artist, title)

        enriched = metadata.copy()

        if not discogs_results:
            print("No Discogs data to enrich.")

        # Aggregate key fields and preserve possible multiple values
        release_years = set()
        countries = set()
        versions = set()

        for item in discogs_results:
            if 'year' in item and item['year']:
                release_years.add(item['year'])
            if 'country' in item and item['country']:
                countries.add(item['country'])
            title_lc = item.get('title', '').lower()
            if 'version' in title_lc or 'remaster' in title_lc or 'reissue' in title_lc:
                versions.add(title_lc)

        # Add enriched fields as new keys with possible multiple values
        if release_years:
            enriched['Discogs_Release_Years'] = sorted(release_years)
        if countries:
            enriched['Discogs_Countries'] = sorted(countries)
        if versions:
            enriched['Discogs_Versions'] = sorted(versions)

        print(f"Enriched metadata with Discogs data (provenance preserved):\n{enriched}")

        # Also enrich using MusicBrainz
        mb_data = self.query_musicbrainz(metadata.get('Title'), metadata.get('Artist'))
        for key, value in mb_data.items():
            if value:
                key_name = f"MusicBrainz_{key.replace(' ', '_')}"
                enriched[key_name] = value

        return enriched

    def batch_enrich(self, metadatas: list[dict]) -> list[dict]:
        enriched_list = []
        for metadata in metadatas:
            enriched = self.enrich_metadata(metadata)
            enriched_list.append(enriched)
            time.sleep(1)  # respect rate limits
        return enriched_list
