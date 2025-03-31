# webapp/views.py
from django.shortcuts import render
from urllib.parse import unquote
from .model import Program, Concert, Composer, Conductor, Soloist, Movement, list_program_ids_by_venue, execute_query


def program_view(request, program_id):
    program = Program.get(program_id)
    return render(request, 'program.html', {"program": program})


def concert_view(request, concert_id):
    concert = Concert.get(concert_id)
    return render(request, 'concert.html', {"concert": concert, "external_links": concert.external_links()})


def program_list_view(request):
    venue = request.GET.get('venue', '')
    programs = []
    program_ids = list_program_ids_by_venue(venue)
    for (program_id, season, orchestra) in program_ids:
        programs.append({
            'id': program_id,
            'season': season,
            'orchestra': orchestra,
        })
    # Sort programs by season
    programs.sort(key=lambda x: x['season'])
    return render(request, 'program_list.html', {
        'programs': programs,
        'selected_venue': venue
    })


def sparql_query_view(request):
    results = None
    query = request.POST.get('query', '')

    if request.method == 'POST' and query:
        try:
            results = execute_query(query)
        except Exception as e:
            results = {'error': str(e)}

    return render(request, 'sparql_query.html', {
        'query': query,
        'results': results
    })


def composer_view(request, composer_uri):
    decoded_uri = unquote(composer_uri)  # Decode the URL-encoded URI
    composer = Composer.get(decoded_uri)
    context = {
        "artist": composer,
        "artist_type": "Composer",
        "additional_info": {
            "Country": composer.mb_country if composer else None,
            "MusicBrainz": composer.mb_uri if composer else None,
            "Disambiguation": composer.mb_disambiguation if composer else None
        }
    }
    return render(request, 'artist_card.html', context)


def conductor_view(request, conductor_uri):
    decoded_uri = unquote(conductor_uri)  # Decode the URL-encoded URI
    conductor = Conductor.get(decoded_uri)
    context = {
        "artist": conductor,
        "artist_type": "Conductor",
        "additional_info": {
            "Country": conductor.mb_country if conductor else None,
            "MusicBrainz": conductor.mb_uri if conductor else None,
            "Disambiguation": conductor.mb_disambiguation if conductor else None
        }
    }
    return render(request, 'artist_card.html', context)


def soloist_view(request, soloist_name):
    soloist = Soloist.get(soloist_name)
    context = {
        "soloist": soloist,
        "additional_info": {
            "Instrument": soloist.soloistInstrument if soloist else None,
            "Roles": soloist.soloistRoles if soloist else None
        }
    }
    return render(request, 'soloist_card.html', context)


def movement_view(request, movement_uri):
    decoded_uri = unquote(movement_uri)
    movement = Movement.get(decoded_uri)

    context = {
        "movement": movement,
        "movement_info": {
            "Title": movement.title if movement else None,
            "Language": movement.language if movement else None,
            "Comment": movement.comment if movement else None,
            "MusicBrainz URI": movement.mb_movement_uri if movement else None,
        },
        "composer": {
            "artist": movement.composer,
            "artist_type": "Composer",
            "additional_info": {
                "Country": movement.composer.mb_country if movement.composer else None,
                "MusicBrainz": movement.composer.mb_uri if movement.composer else None,
                "Disambiguation": movement.composer.mb_disambiguation if movement.composer else None
            }
        } if movement and movement.composer else None
    }
    return render(request, 'movement_card.html', context)
