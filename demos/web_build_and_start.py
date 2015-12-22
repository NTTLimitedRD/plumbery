from plumbery.engine import PlumberyEngine

engine = PlumberyEngine('fittings.yaml')
engine.build_blueprint('web')
engine.start_nodes('web')





