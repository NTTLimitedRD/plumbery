from plumbery.engine import PlumberyEngine

engine = PlumberyEngine('fittings.yaml')
engine.stop_blueprint('web')
engine.destroy_blueprint('web')





