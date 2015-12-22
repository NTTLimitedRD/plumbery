from plumbery.engine import PlumberyEngine

engine = PlumberyEngine('fittings.yaml')
engine.stop_nodes('web')
engine.destroy_blueprint('web')





