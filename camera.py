class Camera:
    def __init__(self, view_width, view_height):
        self.view_width = view_width
        self.view_height = view_height

    def get_position(self, player, track_width, track_height):
        camera_x = int(player.x - self.view_width / 2)
        camera_y = int(player.y - self.view_height / 2)

        if camera_x < 0:
            camera_x = 0

        if camera_y < 0:
            camera_y = 0

        if camera_x > track_width - self.view_width:
            camera_x = track_width - self.view_width

        if camera_y > track_height - self.view_height:
            camera_y = track_height - self.view_height

        return camera_x, camera_y