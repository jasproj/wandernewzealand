#!/usr/bin/env python3
"""
Merge Hermes FareHarbor extraction with existing tours-data.json for WanderNZ.

NZ-specific:
- Filter by location.country = "New Zealand"
- Map city to island/region slug
- Affiliate code: walktheplankadventures
"""

import json
from datetime import datetime
from pathlib import Path

# NZ city to region/slug mapping
NZ_CITIES = {
    'auckland': 'auckland',
    'queenstown': 'queenstown', 
    'rotorua': 'rotorua',
    'wellington': 'wellington',
    'christchurch': 'christchurch',
    'taupo': 'taupo',
    'milford sound': 'milford-sound',
    'bay of islands': 'bay-of-islands',
    'waitomo': 'waitomo',
    'kaikoura': 'kaikoura',
    'dunedin': 'dunedin',
    'hamilton': 'hamilton',
    'napier': 'napier',
    'tauranga': 'tauranga',
    'nelson': 'nelson',
    'wanaka': 'wanaka',
    'franz josef': 'franz-josef',
    'te anau': 'te-anau',
    'paihia': 'bay-of-islands',
    'russell': 'bay-of-islands',
    'kerikeri': 'bay-of-islands',
    'arrowtown': 'queenstown',
    'glenorchy': 'queenstown',
    'picton': 'marlborough',
    'blenheim': 'marlborough',
    'whakatane': 'rotorua',
    'mount maunganui': 'tauranga',
    'raglan': 'hamilton',
    'coromandel': 'coromandel',
    'waiheke island': 'auckland',
    'matamata': 'hamilton',
    'hobbiton': 'hamilton',
}

def normalize_city(city_raw):
    """Map city to slug."""
    city = (city_raw or '').lower().strip()
    return NZ_CITIES.get(city, city.replace(' ', '-'))

def is_new_zealand(item):
    """Check if item is in New Zealand."""
    loc = item.get('location', {}) or {}
    country = (loc.get('country') or '').lower()
    return 'new zealand' in country

# Junk filter patterns
JUNK_PATTERNS = [
    'airport transfer', 'hotel transfer', 'shuttle service',
    'conference room', 'meeting room', 'office space',
    'wedding photography', 'portrait photography',
    'storage locker', 'marina slip',
    'customization fee', 'booking fee', 'service fee',
]

def is_junk(item):
    """Filter out non-tour items."""
    name = (item.get('name') or '').lower()
    for pattern in JUNK_PATTERNS:
        if pattern in name:
            return True
    # Service-only tag
    tags = item.get('tags_name') or ''
    if tags == 'Service' or tags == 'E' or tags == 'Self':
        return True
    return False

# Auto-tagging rules
TAG_RULES = [
    (r'(?i)bungy|bungee', 'Bungy'),
    (r'(?i)skydiv', 'Skydiving'),
    (r'(?i)jet\s*boat', 'Jet Boat'),
    (r'(?i)whale\s*watch', 'Whale Watching'),
    (r'(?i)dolphin', 'Dolphin'),
    (r'(?i)kayak', 'Kayaking'),
    (r'(?i)snorkel', 'Snorkeling'),
    (r'(?i)scuba|dive|diving', 'Scuba'),
    (r'(?i)heli|helicopter', 'Helicopter'),
    (r'(?i)scenic\s*flight', 'Scenic Flight'),
    (r'(?i)wine|vineyard|winery', 'Wine Tour'),
    (r'(?i)hobbit|lord\s*of\s*the\s*rings|lotr', 'Film Location'),
    (r'(?i)maori|cultural', 'Cultural'),
    (r'(?i)glow\s*worm', 'Glowworm'),
    (r'(?i)glacier', 'Glacier'),
    (r'(?i)rafting|raft', 'Rafting'),
    (r'(?i)canyoning|canyon', 'Canyoning'),
    (r'(?i)zip\s*line|zipline', 'Zipline'),
    (r'(?i)sailing|sail\s', 'Sailing'),
    (r'(?i)cruise|cruising', 'Cruise'),
    (r'(?i)fishing', 'Fishing'),
    (r'(?i)hike|hiking|walk|trek', 'Hiking'),
    (r'(?i)bike|cycling|cycle', 'Biking'),
    (r'(?i)surf', 'Surfing'),
    (r'(?i)horse|riding', 'Horse Riding'),
    (r'(?i)farm', 'Farm Tour'),
    (r'(?i)stargazing|dark\s*sky', 'Stargazing'),
    (r'(?i)sunset', 'Sunset'),
    (r'(?i)food|culinary|taste', 'Food Tour'),
    (r'(?i)private', 'Private'),
    (r'(?i)luxury', 'Luxury'),
]

import re

def auto_tag(item):
    """Generate tags from name and headline."""
    tags = []
    text = f"{item.get('name', '')} {item.get('headline', '')}"
    for pattern, tag in TAG_RULES:
        if re.search(pattern, text):
            tags.append({'name': tag, 'shortname': tag.lower().replace(' ', '-')})
    return tags

def build_booking_url(item):
    """Build affiliate booking URL."""
    ref_links = item.get('referral_links', {}) or {}
    if ref_links.get('regular_link'):
        return ref_links['regular_link']
    
    company = item.get('company', {}) or {}
    company_slug = company.get('shortname') or ''
    if company_slug:
        item_id = item.get('id')
        return f"https://fareharbor.com/embeds/book/{company_slug}/items/{item_id}/?asn=fhdn&asn-ref=walktheplankadventures&ref=walktheplankadventures&bookable-only=yes&full-items=yes&marketplace=yes&flow=no"
    return ''

def convert_item(item):
    """Convert FH item to tours-data.json schema."""
    loc = item.get('location', {}) or {}
    company = item.get('company', {}) or {}
    
    # Parse tags from tags_name
    tags_str = item.get('tags_name') or ''
    tags = []
    if tags_str:
        for t in tags_str.split('-'):
            t = t.strip()
            if t and t not in ['E', 'Self', 'Service']:
                tags.append({'name': t, 'shortname': t.lower().replace(' ', '-')})
    
    # Auto-tag if empty
    if not tags:
        tags = auto_tag(item)
    
    return {
        'id': f"fh-{item['id']}",
        'pk': item['id'],
        'name': item.get('name', ''),
        'company': company.get('name', ''),
        'bookingUrl': build_booking_url(item),
        'category': '',
        'location': f"{loc.get('city', '')}, {loc.get('country', '')}".strip(', '),
        'island': normalize_city(loc.get('city', '')),
        'price': None,
        'priceLabel': None,
        'priceConfidence': None,
        'qualityScore': item.get('quality_score'),
        'currency': 'NZD',
        'duration': '',
        'durationText': '',
        'description': item.get('summary') or item.get('headline') or '',
        'descriptionRaw': item.get('summary', ''),
        'descriptionQuality': 'good' if item.get('summary') else 'missing',
        'highlights': [],
        'tags': tags,
        'image': item.get('main_image_url', ''),
        'galleryImages': [],
        'rating': item.get('rating_score'),
        'reviewCount': item.get('rating_review_count'),
        'ratingSource': item.get('rating_provider'),
        'freeCancellation': None,
        'timeOfDay': [],
        'capacity': None,
        'enrichmentSource': 'hermes-fh-api',
        'status': 'active',
        'statusReason': None,
        'statusFirstSeen': None,
        'statusConsecutiveRuns': 0,
        'lastUpdated': datetime.now().isoformat(),
        'needsEnrichment': True,
        '_unknownFields': {
            'durationMinutes': None,
            'availabilityNextWeek': item.get('availability_next_week'),
            'availabilityNext30Days': item.get('availability_next_30days'),
        }
    }

def main():
    repo = Path(__file__).parent.parent
    fh_file = Path.home() / 'Downloads' / 'fareharbor-nz-full.json'
    
    # Load files
    with open(repo / 'tours-data.json') as f:
        current_data = json.load(f)
    with open(fh_file) as f:
        fh_items = json.load(f)
    
    current = current_data.get('tours', [])
    print(f"Current tours: {len(current)}")
    print(f"FH items: {len(fh_items)}")
    
    # Index current by pk
    current_by_pk = {t['pk']: t for t in current if t.get('pk')}
    
    # Filter NZ and junk
    nz_items = []
    non_nz = []
    junk = []
    
    for item in fh_items:
        if not is_new_zealand(item):
            non_nz.append(item)
        elif is_junk(item):
            junk.append(item)
        else:
            nz_items.append(item)
    
    print(f"\nFiltered:")
    print(f"  NZ (keeping): {len(nz_items)}")
    print(f"  Non-NZ: {len(non_nz)}")
    print(f"  Junk: {len(junk)}")
    
    if non_nz:
        print(f"\n=== NON-NZ (sample) ===")
        for item in non_nz[:5]:
            loc = item.get('location', {}) or {}
            print(f"  {item['id']} country={loc.get('country')} - {item.get('name', '')[:40]}")
    
    # Convert and merge
    merged = []
    stats = {'updated': 0, 'new': 0, 'kept': 0}
    
    fh_by_pk = {item['id']: item for item in nz_items}
    
    for item in nz_items:
        pk = item['id']
        if pk in current_by_pk:
            # Exists - merge
            existing = current_by_pk[pk]
            merged_tour = existing.copy()
            
            # Take Hermes data where current is empty
            converted = convert_item(item)
            if not existing.get('galleryImages') and converted.get('galleryImages'):
                merged_tour['galleryImages'] = converted['galleryImages']
            if not existing.get('tags') and converted.get('tags'):
                merged_tour['tags'] = converted['tags']
            if not existing.get('image') and converted.get('image'):
                merged_tour['image'] = converted['image']
            if not existing.get('description') and converted.get('description'):
                merged_tour['description'] = converted['description']
            
            merged_tour['island'] = normalize_city(item.get('location', {}).get('city', ''))
            merged_tour['lastUpdated'] = datetime.now().isoformat()
            merged.append(merged_tour)
            stats['updated'] += 1
        else:
            # New tour
            new_tour = convert_item(item)
            merged.append(new_tour)
            stats['new'] += 1
    
    # Keep current tours not in FH (manually added)
    for pk, t in current_by_pk.items():
        if pk not in fh_by_pk:
            merged.append(t)
            stats['kept'] += 1
    
    print(f"\n=== MERGE STATS ===")
    print(f"Updated: {stats['updated']}")
    print(f"New: {stats['new']}")
    print(f"Kept: {stats['kept']}")
    print(f"Total: {len(merged)}")
    
    # Data quality
    null_price = len([t for t in merged if not t.get('price')])
    null_image = len([t for t in merged if not t.get('image')])
    null_tags = len([t for t in merged if not t.get('tags')])
    needs_enrichment = len([t for t in merged if t.get('needsEnrichment')])
    
    print(f"\n=== DATA QUALITY ===")
    print(f"Null price: {null_price} ({100*null_price/len(merged):.1f}%)")
    print(f"Null image: {null_image} ({100*null_image/len(merged):.1f}%)")
    print(f"Null tags: {null_tags} ({100*null_tags/len(merged):.1f}%)")
    print(f"Needs enrichment: {needs_enrichment}")
    
    # Region distribution
    regions = {}
    for t in merged:
        region = t.get('island') or 'unassigned'
        regions[region] = regions.get(region, 0) + 1
    
    print(f"\n=== REGION DISTRIBUTION (top 15) ===")
    for region, count in sorted(regions.items(), key=lambda x: -x[1])[:15]:
        print(f"  {region}: {count}")
    
    # Output
    output = {
        'schemaVersion': '1.0.8',
        'lastNormalized': datetime.now().strftime('%Y-%m-%d'),
        'tours': merged
    }
    
    out_path = repo / 'tours-data-merged.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nWritten to: {out_path}")

if __name__ == '__main__':
    main()
