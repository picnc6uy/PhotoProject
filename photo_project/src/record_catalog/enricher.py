import time


def _safe_console(text: str) -> str:
    # Avoid Windows console encoding errors by escaping non-CP1252 chars.
    return text.encode("cp1252", "backslashreplace").decode("cp1252")
import requests

class MetadataEnricher:
    """Enriches parsed metadata using external APIs like Discogs and MusicBrainz, preserving original data and provenance."""

    def __init__(self, config):
        self.config = config
        self.discogs_token = config.get("DISCOGS_TOKEN")
        self.musicbrainz_user_agent = config.get("MUSICBRAINZ_USER_AGENT", "RecordCatalogApp/1.0")
        self.use_musicbrainz = str(config.get("USE_MUSICBRAINZ", "true")).lower() != "false"
        self.discogs_disabled = False

    def query_discogs(self, label, catalog_number, artist=None, title=None):
        if self.discogs_disabled:
            return {}
        if not label or not catalog_number:
            print("Discogs enrichment skipped: missing label or catalog number.")
            return {}
        if not self.discogs_token:
            print("Discogs enrichment skipped: missing DISCOGS_TOKEN.")
            return {}
        headers = {"User-Agent": self.musicbrainz_user_agent}
        params = {
            "catno": catalog_number,
            "label": label,
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
        print(
            "Querying Discogs with label='{label}', catalog_number='{catalog_number}', "
            "artist='{artist}', title='{title}'".format(
                label=_safe_console(str(label)),
                catalog_number=_safe_console(str(catalog_number)),
                artist=_safe_console(str(artist)),
                title=_safe_console(str(title)),
            )
        )
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 401:
                    print("Discogs returned 401 Unauthorized. Disabling Discogs for this run.")
                    self.discogs_disabled = True
                    return {}
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 5 * (attempt + 1)
                    print(f"Discogs rate limited (429). Sleeping {delay}s before retry...")
                    time.sleep(delay)
                    continue
                data = response.json()
                if data.get('results'):
                    print(f"Discogs returned {len(data['results'])} result(s)")
                    return data['results']
                print("Discogs returned no results.")
                return {}
            except Exception as e:
                print(f"Discogs API error: {e}")
        return {}

    def query_musicbrainz(self, title, artist):
        if not self.use_musicbrainz:
            return {}
        if not title or not artist:
            return {}
        time.sleep(1)
        url = "https://musicbrainz.org/ws/2/release/"
        params = {
            "query": f'release:{title} AND artist:{artist}',
            "fmt": "json",
            "limit": 1
        }
        headers = {"User-Agent": self.musicbrainz_user_agent}
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 5 * (attempt + 1)
                    print(f"MusicBrainz rate limited (429). Sleeping {delay}s before retry...")
                    time.sleep(delay)
                    continue
                data = response.json()
                if 'releases' in data and data['releases']:
                    release = data['releases'][0]
                    return {
                        "Release Date": release.get('date'),
                        "Country": release.get('country'),
                    }
                return {}
            except Exception as e:
                delay = 4 * (attempt + 1)
                print(f"MusicBrainz API error: {e}. Retrying in {delay}s...")
                time.sleep(delay)
        return {}

    def enrich_metadata(self, metadata: dict) -> dict:
        label = metadata.get('Label Normalized') or metadata.get('Label')
        catalog_number = metadata.get('Catalog Number Normalized') or metadata.get('Catalog Number')
        artist = metadata.get('Artist Normalized') or metadata.get('Artist')
        title = metadata.get('Title Normalized') or metadata.get('Title')
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

        print(
            "Enriched metadata with Discogs data (provenance preserved):\n"
            f"{_safe_console(str(enriched))}"
        )

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
