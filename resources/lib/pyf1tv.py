import json
import re
import os.path
import time
import requests


class PYF1TV:
    """API Adapter for F1TV"""

    def _get_api_key(self):
        """Obtain F1 account api api key"""
        # Download script from f1tv site
        f1_account_script_data = requests.get(
            "https://account.formula1.com/scripts/main.min.js"
        )
        # Use regex to extract apikey
        self.api_key = re.findall('apikey: *"(.*?)"', f1_account_script_data.text)[0]


    def _login(self, username, password):
        # Mostly unrelated, but we must get the users "groupId" and store it - makes little difference but can't hurt
        try:
            self.f1tvapi_group_id = requests.get(
                "https://f1tv.formula1.com/1.0/R/ENG/BIG_SCREEN_HLS/ALL/USER/LOCATION"
            ).json()["resultObj"]["userLocation"][0]["groupId"]
        except KeyError:
            pass

        if self._cacheGetter:
            self.auth_data = self._cacheGetter()

        login_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "RaceControl",
            "apiKey": self.api_key,
            "Content-Type": "application/json",
        }
        data = {"Login": username, "Password": password}
        # Check if we have already stored auth
        if self.auth_data:
            # Check within 23 hours to be safe
            if self.auth_data["time"] <= int(time.time()) - 82800:
                # We need to get new auth:

                self.log("Retrieving and storing new auth")
                auth_data = requests.post(
                    f"{self.f1api}account/subscriber/authenticate/by-password",
                    headers=login_headers,
                    json=data,
                )
                # return the ascendontoken
                self.ascendontoken = auth_data.json()["data"]["subscriptionToken"]
                self.auth_data = {
                    "time": int(time.time()),
                    "token": auth_data.json()["data"]["subscriptionToken"],
                }
                if self._cacheSetter:
                    self._cacheSetter(self.auth_data)

            else:
                # Our existing token is new-enough
                self.log("Using existing auth")
                self.ascendontoken = self.auth_data["token"]
        else:
            # We don't have any auth and so therefore must create & save it.
            self.log("Retrieving and storing new auth")
            auth_data = requests.post(
                f"{self.f1api}account/subscriber/authenticate/by-password",
                headers=login_headers,
                json=data,
            )
            # return the ascendontoken
            self.ascendontoken = auth_data.json()["data"]["subscriptionToken"]
            self.auth_data = {
                "time": int(time.time()),
                "token": auth_data.json()["data"]["subscriptionToken"],
            }

            if self._cacheSetter:
                self._cacheSetter(self.auth_data)

    def __init__(self, username=None, password=None, log=None, cacheGetter=None, cacheSetter=None):
        """Initialising F1TVApp"""
        self.f1api = "https://api.formula1.com/v2/"
        self.f1tvapi = "https://f1tv.formula1.com/2.0/R/ENG/BIG_SCREEN_HLS/"
        self.f1tvplayapi = "https://f1tv.formula1.com/2.0/R/ENG/BIG_SCREEN_HLS/ALL/"
        self.api_key = None
        self.headers = {"User-Agent": "RaceControl"}
        self.ascendontoken = None
        self.f1tvapi_group_id = 14
        self.auth_data = None
        if log:
            self._logfunc = log
        if cacheGetter:
            self._cacheGetter = cacheGetter
        if cacheSetter:
            self._cacheSetter = cacheSetter
        self._get_api_key()

        if username and password:
            self._login(username, password)

    def getImage(self, data):
        try:
            if len(data["metadata"]["pictureUrl"]) > 0:
                url = f"https://ott.formula1.com/image-resizer/image/{data['metadata']['pictureUrl']}?w=1920&h=1080&q=HI&o=L"
                return url
            else:
                #self.log("Error: Did not find image")
                return None
        except:
            return None

    def getDescription(self, data):
        try:
            if len(data["metadata"]["longDescription"]) > 0:
                return data["metadata"]["longDescription"]
            else:
                #self.log("Error: Did not find image")
                return None
        except:
            return None

    def getName(self, data):
        name = None
        if name == None or len(name) == 0:
            try:
                name = data["metadata"]["emfAttributes"]["Global_Title"]
            except:
                pass
        if name == None or len(name) == 0:
            try:
                name = data["metadata"]["emfAttributes"]["Global_Meeting_Name"]   
            except:
                pass

        if name == None or len(name) == 0:
            try:
                name = data["metadata"]["title"]
            except:
                pass
                
        if name == None or len(name) == 0:
            try:
                name = data["metadata"]["longDescription"]
            except:
                pass
                
        if name == None or len(name) == 0:
            try:
                name = data["metadata"]["label"]
            except:
                pass
                
        
        if name == None or len(name) == 0:
            self.log("No name found")
            return None
        else:
            return name



        #self.log(json.dumps(data, indent=4))
        
        # if "metadata" in data:
        #     if "label" in data["metadata"] and data["metadata"]["label"]:
        #         return data["metadata"]["label"]
        #     elif "emfAttributes" in data["metadata"] and "Global_Meeting_Name" in data["metadata"]["emfAttributes"] and data["metadata"]["emfAttributes"]["Global_Meeting_Name"] != "":
        #         return data["metadata"]["emfAttributes"]["Global_Meeting_Name"]
        #     elif "title" in data["metadata"]:
        #         return data["metadata"]["title"]
        #     elif "longDescription" in data["metadata"]:
        #         return data["metadata"]["longDescription"]
        #     else:
        #         self.log("Error: Did not find name")
        #         self.log(json.dumps(data, indent=4))
        #         return None
        #         #exit()
        # else:
        #     self.log("Error: Container did not have metadata")
        #     self.log(json.dumps(data, indent=4))
        #     return None
        #     #exit()
    
    def parseContainer(self, data):

        if "layout" in data:
            if (data["layout"] == "hero" or
                data["layout"] == "title" or
                data["layout"] == "subtitle" or
                data["layout"] == "gp_banner" or
                data["layout"] == "schedule"):
                return None, None

        if "metadata" in data:
            if "label" in data["metadata"] and data["metadata"]["label"]:
                if "Upcoming" in data["metadata"]["label"]:
                    return None, None

        item = {}
        if "events" in data:
            sub_items = []
            for event in data["events"]:
                sub_item, _ = self.parseContainer(event)
                sub_items.append(sub_item)
            return None, sub_items

        if "contentId" in data:
            item["target"] = "PLAY"
            item["uri"] = f"CONTENT/PLAY?contentId={data['id']}"        
        elif "actions" in data and data["actions"][0]["uri"]:
            item["uri"] = data["actions"][0]["uri"]
            item["target"] = data["actions"][0]["targetType"]

        name = self.getName(data)
        if name:
            item["name"] = self.getName(data)

        image_url = self.getImage(data)
        if image_url:
            item["image"] = image_url
        
        description = self.getDescription(data)
        if description:
            item["description"] = description

        if "id" in data:
            item["id"] = data["id"]

        sub_items = []  
        if "retrieveItems" in data:
            for sub_container in data["retrieveItems"]["resultObj"]["containers"]:
                sub_item, _ = self.parseContainer(sub_container)
                if sub_item:
                    sub_items.append(sub_item)

        return item, sub_items

    def log(self, msg):
        if self._logfunc:
            self._logfunc(f"PYF1TV Log: {msg}")

    def getLive(self):
        frontpage_url = (
            f"{self.f1tvapi}ALL/PAGE/395/F1_TV_Pro_Monthly/{self.f1tvapi_group_id}"
        )
        frontpage_data = requests.get(frontpage_url).json()
        for item in frontpage_data["resultObj"]["containers"]:
            if item["layout"] == "hero":
                for container in item["retrieveItems"]["resultObj"]["containers"]:
                    if container["metadata"]["contentSubtype"] == "LIVE":
                        item["target"] = "PLAY"
                        item["uri"] = f"CONTENT/PLAY?contentId={container['id']}"    
                        item["name"] = f"LIVE: {container['metadata']['title']}"
                        item["image"] = self.getImage(container)

                        return item
                        # This is (one of?) the currently live event(s)!
                        # item = {}
                        # item["uri"] = f"/CONTENT/PLAY?contentId={container['id']}"
                        # item["target"] = "PLAY"
                        # item["name"] = f"LIVE: {container['metadata']['title']}"
                        # return item
        
        return None
                    
    def getStreamUrl(self, uri):
        """With a given content_id and optional channel_id, play that by printing the url and launching mpv"""
        url = f"https://f1tv.formula1.com/1.0/R/ENG/BIG_SCREEN_HLS/ALL/{uri}"

        content_headers = {**self.headers, **{"ascendontoken": self.ascendontoken}}

        content_m3u8_request = requests.get(url, params={}, headers=content_headers)
        if content_m3u8_request.ok:
            #self.log(json.dumps(content_m3u8_request.json(), indent=4))
            return content_m3u8_request.json()['resultObj']['url']
        else: 
            return None

    def getContent(self, uri):
        url = f"https://f1tv.formula1.com{uri}"
        data = requests.get(url).json()
        output = []
        if data["resultCode"] == "OK":
            for container in data["resultObj"]["containers"]:
                item, _ = self.parseContainer(container)
                if item:
                    output.append(item)

                if "additionalStreams" in container["metadata"]:
                    for stream in container["metadata"]["additionalStreams"]:
                        item = {}
                        if "driverFirstName" in stream:
                            item["name"] = f"{stream['racingNumber']} - {stream['driverFirstName']} {stream['driverLastName']}"
                        else:
                            item["name"] = stream["title"]
                        item["target"] = "PLAY"
                        item["uri"] = stream["playbackUrl"]
                        output.append(item)
                #else:
                #    return self.get(item)                
        return output

    def getContentItem(self, uri):
        url = f"https://f1tv.formula1.com{uri}"
        data = requests.get(url).json()
        output = []
        if data["resultCode"] == "OK":
            for container in data["resultObj"]["containers"]:
                if "contentId" in container:
                    return self.getContent(uri)
                
                item, sub_items = self.parseContainer(container)
                #self.log(json.dumps(container, indent=4))
                if item:
                    if sub_items:
                        #self.log(sub_items)
                        if "id" in item:
                            item["uri"] = uri
                            item["target"] = "WALL_PAGE_ENTRY"

                    if "name" in item and "target" in item and "uri" in item:
                        output.append(item)
                    else:
                        #self.log(json.dumps(item, indent=4))
                        exit()
                
                            
        return output
        
    def getWallPageEntry(self, uri, id):
        url = f"https://f1tv.formula1.com{uri}"
        data = requests.get(url).json()
        output = []
        if data["resultCode"] == "OK":
            for container in data["resultObj"]["containers"]:
                container_id = None
                if "metadata" in container and "id" in container["metadata"]:
                    container_id = container["metadata"]["id"]
                elif "id" in container:
                    container_id = container["id"]

                if container_id and id == container_id:
                    _, sub_items = self.parseContainer(container)
                    for sub_item in sub_items:
                        output.append(sub_item)

        
        return output


    def getWallPage(self, uri):
        url = f"https://f1tv.formula1.com{uri}"
        data = requests.get(url).json()
        output = []
        sub_output = []
        if data["resultCode"] == "OK":
            for container in data["resultObj"]["containers"]:
                
                item, sub_items = self.parseContainer(container)

                if sub_items:
                    sub_output = sub_items
                    if len(sub_items) == 1:
                        sub_items[0]["name"] = f"{item['name'] - {sub_items[0]['name']}}"
                        item = sub_items[0]
                        
                    elif not "name" in item:
                        self.log(item)
                        output += sub_items
                        item = None
                    elif not "uri" in item:
                        if "id" in item:
                            item["target"] = "WALL_PAGE_ENTRY"
                            item["uri"] = uri
                        else:
                            output += sub_items
                            item = None
                
                if item:
                    output.append(item)

        if len(output) <= 1:
            output = []
            for sub_item in sub_output:
                sub_item["uri"] = uri
                sub_item["target"] = "WALL_PAGE_ENTRY"
                output.append(sub_item)
        return output

    def getPage(self, uri):
        url = f"https://f1tv.formula1.com{uri}"
        data = requests.get(url).json()
        output = []
        sub_output = []
        if data["resultCode"] == "OK":
            for container in data["resultObj"]["containers"]:
                
                item, sub_items = self.parseContainer(container)


                if sub_items:
                    sub_output = sub_items
                    if len(sub_items) == 1:
                        sub_items[0]["name"] = f"{item['name'] - {sub_items[0]['name']}}"
                        item = sub_items[0]
                        
                    elif not "name" in item:
                        self.log(item)
                        output += sub_items
                        item = None
                    elif not "uri" in item:
                        if "id" in item:
                            item["target"] = "WALL_PAGE_ENTRY"
                            item["uri"] = uri
                        else:
                            output += sub_items
                            item = None
                
                if item:
                    output.append(item)

                
        if len(output) <= 1:
            output = []
            for sub_item in sub_output:
                if sub_item:
                    output.append(sub_item)

        return output

    def getMainpage(self):
        return self.getPage(f"/2.0/R/ENG/BIG_SCREEN_HLS/ALL/MENU/F1_TV_Pro_Annual/{self.f1tvapi_group_id}")

    def get(self, item):
        self.log(f"Requested: {json.dumps(item)}")
        if item['target'] == "PAGE":
            return self.getPage(item['uri'])
        elif item['target'] == "WALL_PAGE":
            return self.getWallPage(item['uri'])
        elif item['target'] == "WALL_PAGE_ENTRY":
            return self.getWallPageEntry(item['uri'], item["id"])
        elif item['target'] == "DETAILS_PAGE":
            return self.getContentItem(item['uri'])
        elif item['target'] == "CONTENT":
            return self.getContent(item['uri'])
        elif item['target'] == "PLAY":
            return self.getStreamUrl(item['uri'])