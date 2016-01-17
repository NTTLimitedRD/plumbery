from plumbery.engine import PlumberyEngine

engine = PlumberyEngine('fittings.yaml')
engine.build_blueprint('beachhead control')
engine.start_blueprint('beachhead control')





