from dataclasses import dataclass
import pytmx, pyscroll
from player import*
import pygame

@dataclass
class Portal:
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str

@dataclass
class Map:
    name: str
    walls: list
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals : list
    npcs : list

class MapManager:

    def __init__(self, screen, player):
        self.maps = dict()  #house ->  Map("house", walls, group)
        self.screen = screen
        self.player = player
        self.current_map = "house2"

        self.register_map("world", portals=[
            Portal(from_world="world", origin_point="enter_house", target_world="house", teleport_point="spawn_house"),
            Portal(from_world="world", origin_point="enter_house2", target_world="house2", teleport_point="spawn_house"),
            Portal(from_world="world", origin_point="enter_castle", target_world="base_map", teleport_point="spawn_castle")
        ], npcs=[

            NPC("robin", nb_points=4, dialog=["Bonjour jeune homme, j'ai entendu dire que le roi ","aurait perdu sa couronne, et que quiconque",
                                              "le trouvait obtiendrait moulte richesses.","Je ne sais pas où il se trouve,"
                                              " mais tu devrais"," lui demander.","Pars au nord-est rejoindre la cour","puis continue au nord pour accéder au château","tu trouveras le roi qui te donnera plus d'informations"])



        ])
        self.register_map("house", portals=[
            Portal(from_world = "house", origin_point = "exit_house", target_world = "world", teleport_point = "enter_house_exit")

        ])
        self.register_map("house2", portals=[
            Portal(from_world="house2", origin_point="exit_house", target_world="world", teleport_point="exit_house2")

        ])
        self.register_map("dungeon", portals=[
            Portal(from_world="dungeon", origin_point="enter_rivage", target_world="rivage", teleport_point="spawn_rivage2"),
            Portal(from_world="dungeon", origin_point="enter_world", target_world="world", teleport_point="spawn_world3")

        ], npcs=[
            NPC("boss", nb_points=4, dialog=['Bienvenue dans ma demeure,',' je ne sais pas qui tu es,'," mais tu es le tout premier visiteur de mon antre."
                                             ,"Pour te récompenser, ","Voici une babiole qui est tombé chez moi,","il y a écrit 'couronne' dessus.",
                                             "hmmmmm","Je ne sais pas à quoi ce truc rond signifie,","mais il te servira plus à toi qu'à moi","Probablement..."
                                             ,"Au revoir.","SYSTEME : Quête terminée","SYSTEME : Explorez les environs !"])


        ])
            
        self.register_map("rivage", portals=[
            Portal(from_world="rivage", origin_point="enter_castle", target_world="base_map", teleport_point="spawn_castle3"),
            Portal(from_world="rivage", origin_point="enter_dungeon", target_world="dungeon", teleport_point="spawn_dungeon")

            ], npcs=[

            NPC("noel", nb_points=2, dialog=[' Never gonna give you up !',' Never gonna let you down !','Never gonna run around and','DESERT YOU']),
            NPC("cowboy", nb_points=1, dialog=["On dit qu'un être démoniaque","habite dans les souterrains !","pour y accéder","il suffirait de sauter",
                                               "dans le bon fossé","Argh","Personnellement, je passe mon tour","Et puis...","J'y gagnerai quoi?"])


        ])
        
        self.register_map("base_map", portals=[
            Portal(from_world="base_map", origin_point="enter_world", target_world="world", teleport_point="spawn_world2"),
            Portal(from_world="base_map", origin_point="enter_interieur", target_world="interieur", teleport_point="spawn_interieur"),
            Portal(from_world="base_map", origin_point="enter_rivage", target_world="rivage", teleport_point="spawn_rivage")
            ])
        self.register_map("interieur", portals=[
            Portal(from_world="interieur", origin_point="enter_castle", target_world="base_map", teleport_point="spawn_castle2")
        ], npcs=[
            NPC("paul", nb_points=4, dialog=["(Mais où se trouve cette fichue couronne...)", "Ah, mais je vois qu'une personne veut me parler,"," quelle en est la raison ? ",
                                             "TU veux trouver ma couronne ?"," Laisse moi rire...","Mais bon, si tu y tiens tant, ","alors je veux te donner une indication : "
                                             ,"Pars vers l'est,","En sortant de mon château", "tu y trouveras une plage","c'est là-bas où je l'ai perdue."
                                             ,"Je n'en sais pas plus, maintenant va-t-en !"]),


        ])
        self.teleport_player("player")
        self.teleport_npcs()


    def check_npc_collisions(self, dialog_box):
        for sprite in self.get_group().sprites():
            if sprite.feet.colliderect(self.player.rect)and type(sprite) is NPC:
                dialog_box.execute(sprite.dialog)


    def check_collision(self):
        # portails
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_objects(portal.origin_point)
                rect = pygame.Rect(point.x ,point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.teleport_player(copy_portal.teleport_point)


        # collision
        for sprite in self.get_group().sprites():

            if type(sprite) is NPC:
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0
                else:
                    sprite.speed = 1

            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()



    def teleport_player(self, name):
        point = self.get_objects(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()

    def register_map(self, name, portals=[], npcs=[]):
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame(f"../map/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # définir une liste qui va stocker les rectangles de collision
        walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)
        group.add(self.player)

        # récupérer tous les NPCS pour les ajouter au groupe
        for npc in npcs:
            group.add(npc)

        # enregistrer la nouvelle map chargée
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)


    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self):
        return self.get_map().walls

    def get_objects(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)


    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs

            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()




    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)


    def update(self):
        self.get_group().update()
        self.check_collision()

        for npc in self.get_map().npcs:
            npc.move()