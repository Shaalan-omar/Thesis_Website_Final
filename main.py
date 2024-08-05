from matplotlib import pyplot as plt
import streamlit as st
import cv2
import numpy as np

# Define the functions
def process_image(image):
    angleR = ''
    verticalR = ''
    overR = ''
    apexR = ''
    angleL = ''
    verticalL = ''
    overL = ''
    apexL = ''
    impactL = True
    impactR = True

    # preprocessing 
    image_file_resized = preproc(image)

    if image_file_resized is None:
        st.error("Failed to load the pre-processed image.")
        return impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL
    
    if image_file_resized is not None:
        st.write("Image successfully preprocessed and loaded.")

        # vertical height 
        impactL, impactR, verticalR, verticalL = vertHe(image_file_resized, impactL, impactR, verticalR, verticalL)
        st.progress(20)
        st.write("Vertical height processed.")
        st.write(f"Left Vertical: {verticalL}, Right Vertical: {verticalR}")

        # angulation
        angleR, angleL = angl(image_file_resized, impactL, impactR, angleR, angleL)
        st.progress(40)
        st.write("Angulation processed.")
        st.write(f"Left Angle: {angleL}, Right Angle: {angleR}")

        # Overlap
        overR, overL = over(image_file_resized, impactL, impactR, overR, overL)
        st.progress(60)
        st.write("Overlap processed.")
        st.write(f"Left Overlap: {overL}, Right Overlap: {overR}")

        # Apex Position
        apexR, apexL = apex(image_file_resized, impactL, impactR, apexR, apexL)
        st.progress(80)
        st.write("Apex position processed.")
        st.write(f"Left Apex: {apexL}, Right Apex: {apexR}")

    else:
        st.error("Failed to load the pre-processed image.")

    return impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL



def preproc(image_file):
    # img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # resizing
    resized = cv2.resize(image_file, (780, 540), interpolation=cv2.INTER_LINEAR)
    cv2.imwrite('resized.jpg', resized)
    return resized



def vertHe(original_image, impactL, impactR, verticalR, verticalL):
    image = original_image.copy()

    # Detecting the left canine and drawing the ellipse
    left_color = np.array([0, 255, 0])  # Green
    color_tolerance = 40
    lower_left = left_color - color_tolerance
    upper_left = left_color + color_tolerance
    mask = cv2.inRange(image, lower_left, upper_left)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    lower_tip_y = None

    if contours:
        main_contour = max(contours, key=cv2.contourArea)

        lowest_point = None
        highest_point = None

        for point in main_contour:
            x, y = point[0]

            if lowest_point is None or y > lowest_point[1]:
                lowest_point = (x, y)

            if highest_point is None or y < highest_point[1]:
                highest_point = (x, y)

        if lowest_point:
            cv2.circle(image, lowest_point, 3, (100, 100, 192), -1) 

        if highest_point:
            cv2.circle(image, highest_point, 3, (100, 100, 192), -1)

        lower_tip_y = lowest_point[1]
    else :
        st.write("No left canine detected")

    # Detecting the blue bounding box
    blue_color = np.array([255, 0, 0])
    color_tolerance = 25
    mask_blue = cv2.inRange(image, blue_color - color_tolerance, blue_color + color_tolerance)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours_blue:
        largest_contour_blue = max(contours_blue, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour_blue)
        if h <  80:
            y = y - (80 - h)
            h = 80
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 165, 255), 2)

            lower_boundary_y = y + h
            height = lower_boundary_y - y  
            first_section_height = int(0.34 * height)
            middle_section_height = int(0.58 * height)
            last_section_height = int(0.08 * height)
            mid1_y = y + first_section_height  
            mid2_y = mid1_y + middle_section_height  
            top_boundary_y = y  

            cv2.line(image, (x, lower_boundary_y), (x + w, lower_boundary_y), (255, 0, 0), 2)  
            cv2.line(image, (x, mid1_y), (x + w, mid1_y), (0, 0, 255), 2)  
            cv2.line(image, (x, mid2_y), (x + w, mid2_y), (0, 255, 255), 2)  
            cv2.line(image, (x, top_boundary_y), (x + w, top_boundary_y), (255, 255, 0), 2)

            if lower_tip_y is not None:
                if lower_tip_y >= mid2_y:
                    impactL = False
                elif lower_tip_y < mid2_y and lower_tip_y >= mid1_y-4:
                    verticalL = "Good"
                elif lower_tip_y < mid1_y-4 and lower_tip_y > top_boundary_y+2:
                    verticalL = "Average"
                elif lower_tip_y <= top_boundary_y+2:
                    verticalL = "Poor"
        else:
                
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 165, 255), 2)

            lower_boundary_y = y + h
            height = lower_boundary_y - y  
            first_section_height = int(0.34 * height)
            middle_section_height = int(0.58 * height)
            last_section_height = int(0.08 * height)
            mid1_y = y + first_section_height  
            mid2_y = mid1_y + middle_section_height  
            top_boundary_y = y  

            cv2.line(image, (x, lower_boundary_y), (x + w, lower_boundary_y), (255, 0, 0), 2)  
            cv2.line(image, (x, mid1_y), (x + w, mid1_y), (0, 0, 255), 2)  
            cv2.line(image, (x, mid2_y), (x + w, mid2_y), (0, 255, 255), 2)  
            cv2.line(image, (x, top_boundary_y), (x + w, top_boundary_y), (255, 255, 0), 2)

            if lower_tip_y is not None:
                if lower_tip_y >= mid2_y:
                    impactL = False
                elif lower_tip_y < mid2_y and lower_tip_y >= mid1_y-1:
                    verticalL = "Good"
                elif lower_tip_y < mid1_y-1 and lower_tip_y > top_boundary_y+2:
                    verticalL = "Average"
                elif lower_tip_y <= top_boundary_y+2:
                    verticalL = "Poor"
    else:
        st.write("No blue bounding box detected")
        
    right_color = np.array([255, 0, 255])  
    color_tolerance2 = 25
    mask_right = cv2.inRange(image, right_color - color_tolerance2, right_color + color_tolerance2)
    contours_right, _ = cv2.findContours(mask_right, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lower_tip_y = None

    if contours_right:
        main_contour = max(contours_right, key=cv2.contourArea)

        lowest_point = None
        highest_point = None

        for point in main_contour:
            x, y = point[0]

            if lowest_point is None or y > lowest_point[1]:
                lowest_point = (x, y)

            if highest_point is None or y < highest_point[1]:
                highest_point = (x, y)

        if lowest_point:
            cv2.circle(image, lowest_point, 3, (100, 100, 192), -1)

        if highest_point:
            cv2.circle(image, highest_point, 3, (100, 100, 192), -1)

        lower_tip_y = lowest_point[1]
    else:
        st.write("No right canine detected")
    cayan_color = np.array([255, 255, 0])
    color_tolerance = 40
    mask_cayan = cv2.inRange(image, cayan_color - color_tolerance, cayan_color + color_tolerance)
    contours_cayan, _ = cv2.findContours(mask_cayan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours_cayan:
        largest_contour_cayan = max(contours_cayan, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour_cayan)
        if h <  80:
            y = y - (80 - h)
            h = 80
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
            
            lower_boundary_y = y + h
            height = lower_boundary_y - y  
            first_section_height = int(0.36 * height)
            middle_section_height = int(0.48 * height)
            last_section_height = int(0.34 * height)
            mid1_y = y + first_section_height  
            mid2_y = mid1_y + middle_section_height  
            top_boundary_y = y  

            cv2.line(image, (x, lower_boundary_y), (x + w, lower_boundary_y), (255, 0, 0), 2)  
            cv2.line(image, (x, mid1_y), (x + w, mid1_y), (0, 0, 255), 2)  
            cv2.line(image, (x, mid2_y), (x + w, mid2_y), (0, 255, 255), 2)  
            cv2.line(image, (x, top_boundary_y), (x + w, top_boundary_y), (255, 255, 0), 2) 
            
            if lower_tip_y is not None:
                if lower_tip_y >= mid2_y:
                    impactR = False
                elif lower_tip_y < mid2_y and lower_tip_y >= mid1_y-4:
                    verticalR = "Good"
                elif lower_tip_y < mid1_y-4 and lower_tip_y >= top_boundary_y:
                    verticalR = "Average"
                elif lower_tip_y < top_boundary_y:
                    verticalR = "Poor"
        else:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
            
            lower_boundary_y = y + h
            height = lower_boundary_y - y  
            first_section_height = int(0.3 * height)
            middle_section_height = int(0.48 * height)
            last_section_height = int(0.34 * height)
            mid1_y = y + first_section_height
            mid2_y = mid1_y + middle_section_height  
            top_boundary_y = y  

            cv2.line(image, (x, lower_boundary_y), (x + w, lower_boundary_y), (255, 0, 0), 2)  
            cv2.line(image, (x, mid1_y), (x + w, mid1_y), (0, 0, 255), 2)  
            cv2.line(image, (x, mid2_y), (x + w, mid2_y), (0, 255, 255), 2)  
            cv2.line(image, (x, top_boundary_y), (x + w, top_boundary_y), (255, 255, 0), 2) 
            
            if lower_tip_y is not None:
                if lower_tip_y >= mid2_y:
                    impactR = False
                elif lower_tip_y < mid2_y and lower_tip_y >= mid1_y-2:
                    verticalR = "Good"
                elif lower_tip_y < mid1_y-2 and lower_tip_y >= top_boundary_y+1:
                    verticalR = "Average"
                elif lower_tip_y < top_boundary_y+1:
                    verticalR = "Poor"
    else:
        st.write("No cayan bounding box detected")
        
    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')  # this will hide the x-axis and y-axis
    st.write("Please find the Vertical Height below:")
    st.pyplot(fig)
    return impactL, impactR, verticalR, verticalL


def angl(original_image,impactL,impactR,angleR,angleL):
    image =original_image.copy()
    # Define the tolerance range for the color (adjustable)
    color_tolerance = 40
    color_tolerance2 = 25
    
    #Left Canine 
    if impactL :
        left_color = np.array([0,255, 0])  # BGR format Green
        lower_left = left_color - color_tolerance
        upper_left = left_color + color_tolerance
        mask= cv2.inRange(image, lower_left, upper_left)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # If contours are found
        if contours:
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            # Fit an ellipse to the contour
            if largest_contour.size > 10:
                
                ellipse = cv2.fitEllipse(largest_contour)
                
                # Extract the angle of inclination from the fitted ellipse
                angle = ellipse[2]
                if angle >90 :
                    angle=180-angle
                
                # # Display the angle
                # print(f"Angle of inclination: {angle} degrees")
                center_x, center_y = map(int, ellipse[0])
                
                # Draw the ellipse on the original image
                cv2.ellipse(image, ellipse, (0, 255, 0), 2)
                
                # Calculate the endpoints for the main axis of the ellipse
                main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
                x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
                y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))
        
                # Draw the main axis of the ellipse
                cv2.line(image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))), 
                                int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
                        (x_main, y_main), (255, 0, 0), 2)
                    # Draw the y-axis from the center of the ellipse
                cv2.line(image, (center_x, 10), (center_x, image.shape[0]), (255, 255, 255), 2)
        
                 # Write the angle text on the image
                y_axis_height = 300  # Change this value to your desired height
                y_axis_top = max(0, center_y - (y_axis_height // 2))
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_color = (255, 255, 255)  # White color
                font_thickness = 2
                angle_text = f"Angle: {angle.__round__(3)} degrees"
                text_size = cv2.getTextSize(angle_text, font, font_scale, font_thickness)[0]
                text_x = center_x + 70
                text_y = center_y - 75
        
                cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
                if angle<=(10):
                    angleL="Good"
                elif angle>(10) and angle<=(25):
                    angleL="Average"
                elif angle>(25):
                    angleL="Poor"
        else:
            st.write("No left canine detected")
    #Right Canine 
    if impactR : 
        right_color = np.array([255, 0, 255])  # BGR format Pink
        lower_right = right_color - color_tolerance2
        upper_right = right_color + color_tolerance2
        mask2= cv2.inRange(image, lower_right, upper_right)
        contours2, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours2:
            # Get the largest contour
            largest_contour = max(contours2, key=cv2.contourArea)
            # Fit an ellipse to the contour
            if largest_contour.size > 10:
                
                ellipse = cv2.fitEllipse(largest_contour)
                
                # Extract the angle of inclination from the fitted ellipse
                angle = ellipse[2]
                
                angle = 180 - angle
                if angle >90 :
                    angle=180-angle
                # # Display the angle
                # print(f"Angle of inclination: {angle} degrees")
                center_x, center_y = map(int, ellipse[0])
                
                # # Draw the ellipse on the original image
                cv2.ellipse(image, ellipse, (0, 255, 0), 2)
        
        
                # Calculate the endpoints for the main axis of the ellipse
                main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
                x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
                y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))
        
                # Draw the main axis of the ellipse
                cv2.line(image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))), 
                                int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
                        (x_main, y_main), (255, 0, 0), 2)
                
                         # Write the angle text on the image
                y_axis_height = 300  # Change this value to your desired height
                y_axis_top = max(0, center_y - (y_axis_height // 2))
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_color = (255, 255, 255)  # White color
                font_thickness = 2
                angle_text = f"Angle: {angle.__round__(3)} degrees"
                text_size = cv2.getTextSize(angle_text, font, font_scale, font_thickness)[0]
                text_x = center_x - 200
                text_y = center_y - 80
                cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
                if angle<=(10):
                    angleR="Good"
                elif angle>(10) and angle<=(25):
                    angleR="Average"
                elif angle>(25):
                    angleR="Poor"
        else:
            st.write("No right canine detected")
    
    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')  # this will hide the x-axis and y-axis
    st.write("Please find the Angulation below:")
    st.pyplot(fig)
    return(angleR,angleL)


def over(original_image,impactL,impactR,overR,overL):
    image =original_image.copy()
    # Convert the image to HSV format
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    Right_canine_tip_x=None
    Left_canine_tip_x=None

    if impactL :
        rightmost_x=None
        rightmost_point = None
        # Define the range for blue color in HSV
        lower_blue = np.array([110, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
        # Define the range for green color in HSV
        lower_green = np.array([50, 50, 50])
        upper_green = np.array([70, 255, 255])
        green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
        ####################
        Right_canine_tip_x = None


        if green_contours:
            main_contour = max(green_contours, key=cv2.contourArea)

            # Initialize the lowest and highest points
            lowest_point = None
            highest_point = None
            lowest_x = None
            lowest_y = None

            # Loop through the contour points
            for point in main_contour:
                x, y = point[0]

                 # Check if this point has a lower x value
                if lowest_y is None or y > lowest_y:
                    lowest_x = x
                    lowest_y = y
                    lowest_point = (lowest_x, lowest_y)
                # Check if this point has the same x value and a lower y value
                elif y == lowest_y and (lowest_x is None or x < lowest_x):
                    lowest_x = x
                    lowest_point = (lowest_x, lowest_y)


            # Draw the points on the original image
            if lowest_point:
                cv2.circle(image, lowest_point, 5, (0, 0, 255), -1)  # Draw in red


            Left_canine_tip_x = lowest_point[0]
            
            # Check if Rightmost point is found

                ###########################
            for contour in blue_contours:
                if cv2.contourArea(contour) > 100:  # Filter out small contours
                    ellipse = cv2.fitEllipse(contour)
                    cv2.ellipse(image, ellipse, (255, 0, 0), 2)  # Blue ellipse
                    Left_center_x, Left_center_y = map(int, ellipse[0])
                    center = ellipse [0]
                    axes = ellipse[1]
                    angle = ellipse[2]
                    angle_rad = np.radians(angle - 90)
                    major_axis_length = max(axes) / 2
                    rightmost_x = center[0] + major_axis_length * np.cos(angle_rad)


            # Calculate the endpoints for the main axis of the ellipse
                    Left_main_axis_length = int(ellipse[1][1] / 2)  # Half the length of the minor axis
                    Left_x_main = int(Left_center_x - Left_main_axis_length * np.sin(np.radians(ellipse[2])))
                    Left_y_main = int(Left_center_y + Left_main_axis_length * np.cos(np.radians(ellipse[2])))

                    # Draw the main axis of the ellipse
                    cv2.line(image, (int(ellipse[0][0] + Left_main_axis_length * np.sin(np.radians(ellipse[2]))), 
                                int(ellipse[0][1] - Left_main_axis_length * np.cos(np.radians(ellipse[2])))),
                        (Left_x_main, Left_y_main), (0, 255, 0), 2)
        else:
            st.write("No left canine detected")
        ###################
               
        if Left_canine_tip_x is not None and rightmost_x is not None and Left_center_x is not None: 
            if Left_canine_tip_x - 1>= rightmost_x:
                overL = "Good"
            elif rightmost_x > Left_canine_tip_x - 1 > Left_center_x:
                overL = "Average"
            elif Left_canine_tip_x - 1 <= Left_center_x:
                overL = "Poor"
    if impactR:
        #pink
        leftmost_x=None
        leftmost_point=None
        pink_color=np.array([255, 0, 255])  # BGR format Pink
        color_tolerance = 40
        color_tolerance2 = 25
        pink_lower = pink_color - color_tolerance2
        pink_upper = pink_color + color_tolerance2
        pink_mask = cv2.inRange(image, pink_lower, pink_upper)
        pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #cyan
        cyan_lower = np.array([85, 100, 100])
        cyan_upper = np.array([95, 255, 255])
        cyan_mask = cv2.inRange(hsv_image, cyan_lower, cyan_upper)
        cyan_contours, _ = cv2.findContours(cyan_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        Right_canine_tip_x = None
        if pink_contours :
            main_contour = max(pink_contours, key=cv2.contourArea)

            # Initialize the lowest and highest points
            lowest_point = None
            highest_point = None
            lowest_x = None
            lowest_y = None

            # Loop through the contour points
            for point in main_contour:
                x, y = point[0]

                 # Check if this point has a lower x value
                if lowest_y is None or y > lowest_y:
                    lowest_x = x
                    lowest_y = y
                    lowest_point = (lowest_x, lowest_y)
                # Check if this point has the same x value and a lower y value
                elif y == lowest_y and (lowest_x is None or x > lowest_x):
                    lowest_x = x
                    lowest_point = (lowest_x, lowest_y)


            # Draw the points on the original image
            if lowest_point:
                cv2.circle(image, lowest_point, 5, (0, 0, 255), -1)  # Draw in red


            Right_canine_tip_x = lowest_point[0]

         # cyan contours
        else:
            st.write("No right canine detected")
            
        for contour in cyan_contours:
            if cv2.contourArea(contour) > 100:  # Filter out small contours
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(image, ellipse, (255, 0, 0), 2)  # Blue ellipse
                Right_center_x,Right_center_y = map(int, ellipse[0])
                #######
                center = ellipse[0]
                axes = ellipse[1]
                angle = ellipse[2]
                angle_rad = np.radians(angle - 90)
                major_axis_length = max(axes) / 2
                leftmost_x = center[0] - major_axis_length * np.cos(angle_rad)

             # Calculate the endpoints for the main axis of the ellipse
                Right_main_axis_length = int(ellipse[1][1] / 2)  # Half the length of the minor axis
                Right_x_main = int(Right_center_x - Right_main_axis_length * np.sin(np.radians(ellipse[2])))
                Right_y_main = int(Right_center_y + Right_main_axis_length * np.cos(np.radians(ellipse[2])))

                # Draw the main axis of the ellipse
                cv2.line(image, (int(ellipse[0][0] + Right_main_axis_length * np.sin(np.radians(ellipse[2]))), 
                            int(ellipse[0][1] - Right_main_axis_length * np.cos(np.radians(ellipse[2])))),
                    (Right_x_main, Right_y_main), (0, 255, 0), 2)

        if Right_canine_tip_x is not None and leftmost_x is not None and Right_center_x is not None:
            if (Right_canine_tip_x + 1 ) <= leftmost_x:
                overR = "Good"
            elif  leftmost_x < (Right_canine_tip_x + 1 ) < Right_center_x:
                overR = "Average"
            elif (Right_canine_tip_x + 1 ) >= Right_center_x :
                overR = "Poor"
    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')  # this will hide the x-axis and y-axis
    st.write("Please find the Overlap below:")
    st.pyplot(fig)
    return(overR,overL)


def apex(original_image,impactL,impactR,apexR,apexL):
    image = original_image.copy()
    # Define the tolerance range for the color (adjustable)
    color_tolerance = 40
    color_tolerance2 = 25

    if impactL:
        L_canine = np.array([0, 255 , 0])  # BGR format
        # Define lower and upper bounds for the color with tolerance
        lower_L_Canine = L_canine - color_tolerance
        upper_L_Canine = L_canine + color_tolerance
        mask_L_Canine= cv2.inRange(image, lower_L_Canine, upper_L_Canine)
        # Find contours in the masked image
        contours_L_Canine, _ = cv2.findContours(mask_L_Canine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours_L_Canine:
            # Get the largest contour
            largest_contour = max(contours_L_Canine, key=cv2.contourArea)
            
            # Fit an ellipse to the largest contour
            ellipse = cv2.fitEllipse(largest_contour)
             # Get the parameters of the fitted ellipse
            center, axes, angle = ellipse
            angle=180-angle
            
            # Calculate the topmost point of the ellipse
            # The topmost point will be at (center_x, center_y - major_axis_length / 2) considering the angle
            center_x, center_y = center
            major_axis_length = max(axes)
            
            # Convert the angle to radians
            angle_rad = np.deg2rad(angle)
            if major_axis_length <80:
                major_axis_length = 80

            # Calculate the topmost point of the ellipse
            topmost_point_x = int(center_x - (major_axis_length / 2) * np.sin(angle_rad))
            topmost_point_y = int(center_y - (major_axis_length / 2) * np.cos(angle_rad))
            L_apex_position = topmost_point_x
            topmost_point = (topmost_point_x, topmost_point_y)            
            cv2.ellipse(image, ellipse, (0, 255, 0), 2)
            cv2.circle(image, topmost_point, 5, (255, 0, 0), -1)

            
            L_apex_position = topmost_point[0]

            if angle < 90:
                angle_test = angle
            else:
                angle_test = abs(180 - angle)
                
            if angle_test <= 10:
                apexL='Good'
            elif angle_test > 10 and angle_test <= 38:
                apexL='Average'
            elif angle_test > 38:
                apexL= 'Poor'
        else:
            st.write("No left canine detected")

    if impactR :
        R_first_premolar = np.array([128, 0, 128])  # BGR format
        R_second_premolar = np.array([0, 165, 255])  # BGR format
        R_canine = np.array([255, 0, 255])  # BGR format


        # Define lower and upper bounds for the color with tolerance
        lower_R_Canine = R_canine - color_tolerance
        upper_R_Canine = R_canine + color_tolerance
        mask_R_Canine= cv2.inRange(image, lower_R_Canine, upper_R_Canine)
        # Find contours in the masked image
        contours_R_Canine, _ = cv2.findContours(mask_R_Canine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours_R_Canine:
            # Get the largest contour
            largest_contour = max(contours_R_Canine, key=cv2.contourArea)
            
            # Fit an ellipse to the largest contour
            ellipse = cv2.fitEllipse(largest_contour)
            
            # Get the parameters of the fitted ellipse
            center, axes, angle = ellipse
            
            # Calculate the topmost point of the ellipse
            # The topmost point will be at (center_x, center_y - major_axis_length / 2) considering the angle
            center_x, center_y = center
            major_axis_length = max(axes)
            
            # Convert the angle to radians
            angle_rad = np.deg2rad(angle)
            if major_axis_length <80:
                major_axis_length = 80
            
            # Calculate the topmost point of the ellipse
            topmost_point_x = int(center_x - (major_axis_length / 2) * np.sin(angle_rad))
            topmost_point_y = int(center_y - (major_axis_length / 2) * np.cos(angle_rad))
            R_apex_position = topmost_point_x
            topmost_point = (topmost_point_x, topmost_point_y)            
            cv2.ellipse(image, ellipse, (0, 255, 0), 2)
            cv2.circle(image, topmost_point, 5, (255, 0, 0), -1)
            
            R_apex_position = topmost_point[0]

            if angle < 90:
                angle_test = angle
            else:
                angle_test = abs(180 - angle)
                
            if angle_test <= 10:
                apexR='Good'
            elif angle_test > 10 and angle_test <= 33:
                apexR='Average'
            elif angle_test > 33:
                apexR= 'Poor'
        else:
            st.write("No right canine detected")
            
    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')  # this will hide the x-axis and y-axis
    st.write("Please find the Apex Position below:")
    st.pyplot(fig)               
    return apexR, apexL


#Recommandation 
def recomend(impact,angle,apex,vertical,over):
    #All 4 Good
    if angle=="Good" and apex=="Good" and vertical=="Good" and over=="Good":
           print("Straight Forward Impaction")
           return "Straight Forward Impaction"
    #Apex Position Average
    elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Good":
           print("Mildly Difficult Impaction")
           return "Mildly Difficult Impaction"
    #Apex Position Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Good" and over=="Good":
           print("Mildly Difficult Impaction")
           return "Mildly Difficult Impaction"
    
    
    #overlap Average
    elif angle=="Good" and apex=="Good" and vertical=="Good" and over=="Average":
           print("Mildly Difficult Impaction")
           return "Mildly Difficult Impaction"
    #overlap  and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Average":
           print("Mildly Difficult Impaction")
           return "Mildly Difficult Impaction"
    #overlap Average and Apex Poor
    elif angle=="Good" and apex=="poor" and vertical=="Good" and over=="Average":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    
    
    #overlap poor
    elif angle=="Good" and apex=="Good" and vertical=="Good" and over=="Poor":
           print("Mildly Difficult Impaction")
           return "Mildly Difficult Impaction"
    #overlap poor and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Poor":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #overlap poor and Apex Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Good" and over=="Poor":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    
    
    #Vertical Height Average
    elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Good":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #Vertical Height and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Good":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #Vertical Height Average and Apex poor 
    elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Good":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    
    
    #Vertical Height and Overlap Average
    elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Averge":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #Vertical Height and Apex and Overlap Average
    elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Average":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #Vertical Height and Overlap Average and  Apex Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Average":
           print("Difficult Impaction")
           return "Difficult Impaction"
    
    
    #Vertical Height Average and Overlap Poor
    elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Poor":
           print("Moderately Difficult Impaction")
           return "Moderately Difficult Impaction"
    #Vertical Height and Apex Average and Overlap Poor
    elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Poor":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Average and Apex and Overlap Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Poor":
           print("Difficult Impaction")
           return "Difficult Impaction"
    
    
    #Vertical Height Poor
    elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Good":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Good":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and Apex Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Good":
           print("Difficult Impaction")
           return "Difficult Impaction"
    
    #Vertical Height Poor and overlap average
    elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Average":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and overlap average and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Average":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and overlap average and Apex Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Average":
           print("Difficult Impaction")
           return "Difficult Impaction"
    
    #Vertical Height Poor and overlap poor
    elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Poor":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and overlap poor and Apex Average
    elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Poor":
           print("Difficult Impaction")
           return "Difficult Impaction"
    #Vertical Height Poor and overlap poor and Apex Poor
    elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Poor":
           print("Difficult Impaction")
           return "Difficult Impaction"
    
    
    #angle average 
    elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Good":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    #angle average apex average
    elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Good":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    #angle average and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Good":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    
    
    #angle average and overlap averge 
    elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Average":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    ##angle average and overlap averge  apex average
    elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Average":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    ##angle average and overlap averge  and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    
    
    #angle average and overlap poor 
    elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Poor":
        print("Moderately Difficult Impaction")
        return "Moderately Difficult Impaction"
    ##angle average and overlap poor  apex average
    elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    ##angle average and overlap poor  and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    
    
    #angle average and vetical average
    elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical average apex average
    elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical average and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"


     #angle average and vetical and overlap average
    elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical and overlap average apex average
    elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical and overlap average and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"


      #angle average and vetical average and overlap poor
    elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical average apex average and overlap poor
    elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical average and apex poor and overlap poor
    elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"


    #angle average and vetical poor
    elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical poor apex average
    elif angle=="Average" and apex=="Average" and vertical=="Poor"  and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical poor and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Poor"  and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"


     #angle average and vetical poor and overlap average
    elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and veticalpoor and overlap average apex average
    elif angle=="Average" and apex=="Average" and vertical=="Poor" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical poor and overlap average and apex poor
    elif angle=="Average" and apex=="Poor" and vertical=="Poor" and over=="Average":
        print("Complicated Impaction")
        return "Complicated Impaction"


      #angle average and vetical poor and overlap poor
    elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle average and vetical poor apex average and overlap poor
    elif angle=="Average" and apex=="Average" and vertical=="Poor" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle average and vetical poor and apex poor and overlap poor
    elif angle=="Average" and apex=="Poor" and vertical=="Poor" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"


    #angle poor 
    elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"


    #angle poor and overlap average
    elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and overlap average and apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and overlap average and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"


    #angle poor and overlap poor
    elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Poor":
        print("Difficult Impaction")
        return  "Difficult Impaction"
    #angle poor and overlap poor and apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and overlap poor and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"


    #angle poor and vertical average
    elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and vertical average apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and vertical average and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Good":
        print("Difficult Impaction")
        return "Difficult Impaction"


    #angle poor and vertical average and over average
    elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and vertical average and over average apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Average":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and vertical average and over average and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Average":
        print("Complicated Impaction")
        return "Complicated Impaction"


    #angle poor and vertical average and over poor
    elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Poor":
        print("Difficult Impaction")
        return "Difficult Impaction"
    #angle poor and vertical average and over poor apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical average and over poor and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"


    #angle poor and vertical poor
    elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Good":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical poor and apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Good":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical poor and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Good":
        print("Complicated Impaction")
        return "Complicated Impaction"


     #angle poor and vertical poor and over average
    elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Average":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical average and over average apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Average":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical average and over average and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Average":
        print("Complicated Impaction")
        return "Complicated Impaction"


    #angle poor and vertical poor and over poor
    elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical poor and over poor apex average
    elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Poor":
        print("Complicated Impaction")
        return "Complicated Impaction"
    #angle poor and vertical poor and over poor and apex poor
    elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Poor":
        print("Very Complicated Impaction")
        return "Very Complicated Impaction"

    elif not impact:
        print("No Impaction")
        return "No Impaction"


def analyze_image(impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL):
    results = {
        "left": {
            "impact": impactL,
            "angulation": angleL,
            "apex_position": apexL,
            "vertical_height": verticalL,
            "overlapping": overL,
            "recommendation": recomend(impactL, angleL, apexL, verticalL, overL)
        },
        "right": {
            "impact": impactR,
            "angulation": angleR,
            "apex_position": apexR,
            "vertical_height": verticalR,
            "overlapping": overR,
            "recommendation": recomend(impactR, angleR, apexR, verticalR, overR)
        }
    }
    return results

# Streamlit app
st.title("CanineImpactedAI")

uploaded_file = st.file_uploader("Choose an X-ray image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.image(image, caption="Uploaded X-ray image", use_column_width=True)

    st.write("Processing the image...")
    impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL = process_image(image)

    st.write("Processing completed!")
    results = analyze_image(impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL)
    st.json(results)
    
# uploaded_file = cv2.imread('YOLO.jpg')

# st.write("Processing the image...")
# impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL = process_image(uploaded_file)

# st.write("Processing completed!")
# results = analyze_image(impactL, impactR, angleR, verticalR, overR, apexR, angleL, verticalL, overL, apexL)
# st.json(results)

###OLD VERSION LIES BELOW####
# import glob
# import cv2
# import numpy as np
# import os.path
# from roboflow import Roboflow
# import matplotlib.pyplot as plt
# import streamlit as st

# # # Load the image
# # image_path='4.jpg'
# # img = cv2.imread(image_path,cv2.IMREAD_COLOR)

# # Title and instructions
# st.title("Welcome Doctor to موقع اسناني.com")
# st.write("Please upload an image file.")

# # File uploader
# uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# # Display the uploaded image and process it
# if uploaded_file is not None:
#     # Read the uploaded image
#     image_bytes = uploaded_file.read()

#     # Convert the image bytes to a numpy array
#     nparr = np.frombuffer(image_bytes, np.uint8)

#     # Decode the numpy array to an OpenCV image
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # Display the image using Streamlit
#     st.image(img, caption='Uploaded Image', use_column_width=True)

#     #resizing
#     resized = cv2.resize(img, (780, 540), interpolation = cv2.INTER_LINEAR)
#     #sharpen
#     kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
#     image = cv2.filter2D(resized, -1000 ,kernel)
#     cv2.imwrite('resized.jpg',image)

#     #yolo
#     # Initialize Roboflow client
#     rf = Roboflow(api_key="5ZFtB1hrrQTykeWZrSWd")

#     # Load the Roboflow workspace and project
#     workspace = rf.workspace()
#     project = workspace.project("test-labeling-5hhg6")

#     # Select the model version
#     model_version = 4

#     # Load the model from the project
#     model = project.version(model_version).model

#     # Define the color for each class
#     class_colors = {
#         "L_lateral-incisor": (255, 0, 0),  # Blue
#         "L_Canine": (0, 255, 0),            # Green
#         "L_first-premolar": (0, 0, 255),    # Red
#         "L_second-premolar": (0, 255, 255),  # Yellow

#         "R_lateral incisor": (255, 255, 0),  # Cyan
#         "R_Canine": (255, 0, 255),            # Pink
#         "R_first premolar": (128, 0, 128),    # Purple
#         "R_second premolar": (0, 165, 255)  # Orange
#     }

#     # Load the input image
#     input_image_path = "resized.jpg"
#     input_image = cv2.imread(input_image_path)

#     # Make predictions on the input image
#     predictions = model.predict(input_image_path, confidence=40).json()

#     # Loop through the predictions and draw colored segmentations
#     for prediction in predictions["predictions"]:
#         class_name = prediction["class"]
#         color = class_colors.get(class_name, (0, 0, 0))  # Default to black if class not found
#         points = prediction["points"]

#         # Convert points to numpy array of integers
#         points_np = [(int(point["x"]), int(point["y"])) for point in points]
#         points_np = np.array(points_np)

#         # Draw filled polygon
#         original_image=cv2.fillPoly(input_image, [points_np], color)

#     #angulation
#     image =original_image.copy()
#     left_color = np.array([0,255, 0])  # BGR format Green
#     right_color = np.array([255, 0, 255])  # BGR format Pink
#     # Define the tolerance range for the color (adjustable)
#     color_tolerance = 40
#     color_tolerance2 = 25
#     # Define lower and upper bounds for the color with tolerance
#     lower_left = left_color - color_tolerance
#     upper_left = left_color + color_tolerance
#     lower_right = right_color - color_tolerance2
#     upper_right = right_color + color_tolerance2
#     mask= cv2.inRange(image, lower_left, upper_left)
#     mask2= cv2.inRange(image, lower_right, upper_right)
#     # Find contours in the masked image
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours2, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     # If contours are found
#     if contours:
#         # Get the largest contour
#         largest_contour = max(contours, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # Extract the angle of inclination from the fitted ellipse
#             angle = ellipse[2]

#             # Display the angle
#             print(f"Angle of inclination: {angle} degrees")
#             center_x, center_y = map(int, ellipse[0])

#             # Draw the ellipse on the original image
#             cv2.ellipse(image, ellipse, (0, 255, 0), 2)

#             # Calculate the endpoints for the main axis of the ellipse
#             main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
#             x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
#             y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (x_main, y_main), (255, 0, 0), 2)
#                 # Draw the y-axis from the center of the ellipse
#             cv2.line(image, (center_x, 10), (center_x, image.shape[0]), (255, 255, 255), 2)

#             # Write the angle text on the image
#             y_axis_height = 300  # Change this value to your desired height
#             y_axis_top = max(0, center_y - (y_axis_height // 2))
#             font = cv2.FONT_HERSHEY_SIMPLEX
#             font_scale = 0.7
#             font_color = (255, 255, 255)  # White color
#             font_thickness = 2
#             angle_text = f"Angle: {angle.__round__(3)} degrees"
#             text_size = cv2.getTextSize(angle_text, font, font_scale, font_thickness)[0]
#             text_x = center_x + 70
#             text_y = center_y - 75

#             cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
#             if angle<=15:
#                 angleL="Good"
#             elif angle>15 and angle<=30:
#                 angleL="Average"
#             elif angle>30:
#                 angleL="Poor"

#     if contours2:
#         # Get the largest contour
#         largest_contour = max(contours2, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # Extract the angle of inclination from the fitted ellipse
#             angle = ellipse[2]

#             angle = 180 - angle
#             # Display the angle
#             print(f"Angle of inclination: {angle} degrees")
#             center_x, center_y = map(int, ellipse[0])

#             # # Draw the ellipse on the original image
#             cv2.ellipse(image, ellipse, (0, 255, 0), 2)


#             # Calculate the endpoints for the main axis of the ellipse
#             main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
#             x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
#             y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (x_main, y_main), (255, 0, 0), 2)

#                     # Write the angle text on the image
#             y_axis_height = 300  # Change this value to your desired height
#             y_axis_top = max(0, center_y - (y_axis_height // 2))
#             font = cv2.FONT_HERSHEY_SIMPLEX
#             font_scale = 0.7
#             font_color = (255, 255, 255)  # White color
#             font_thickness = 2
#             angle_text = f"Angle: {angle.__round__(3)} degrees"
#             text_size = cv2.getTextSize(angle_text, font, font_scale, font_thickness)[0]
#             text_x = center_x - 200
#             text_y = center_y - 80
#             cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
#             if angle<=15:
#                 angleR="Good"
#             elif angle>15 and angle<=30:
#                 angleR="Average"
#             elif angle>30:
#                 angleR="Poor"

#     if not contours and not contours2:
#         print("No red object found in the image.")
#     else:
#         # Display the image using Matplotlib's imshow function
#         plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         plt.axis('off') # this will hide the x-axis and y-axis
#         plt.show()
#         # save the image
#         cv2.imwrite('angulation.jpg', image)
#         fig, ax = plt.subplots()
#         ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         ax.axis('off')  # this will hide the x-axis and y-axis
#         st.write("Please find the Angulation below:")
#         st.pyplot(fig)  # display the matplotlib plot in Streamlit

#     #Vertical Height
#     image = original_image.copy()

#     # #Detecting the green canine and drawing the ellipse
#     green_color = np.array([0, 255, 0])  # BGR format
#     color_tolerance = 40
#     lower_red = green_color - color_tolerance
#     upper_red = green_color + color_tolerance
#     mask = cv2.inRange(image, lower_red, upper_red)
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours:
#         largest_contour2 = max(contours, key=cv2.contourArea)
#         if largest_contour2.size > 10:
#             ellipse = cv2.fitEllipse(largest_contour2)
#             angle = 180 - ellipse[2]
#             center_x, center_y = map(int, ellipse[0])
#             cv2.ellipse(image, ellipse, (0, 255, 0), 2)
#             main_axis_length = int(ellipse[1][1] / 2)
#             x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
#             y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))

#             cv2.line(image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (x_main, y_main), (0, 0, 0), 2)

#             lower_tip_y = max(ellipse[0][1], y_main)

#             font = cv2.FONT_HERSHEY_SIMPLEX
#             font_scale = 0.7
#             font_color = (255, 255, 255)
#             font_thickness = 2
#             #angle_text = f"Angle: {angle.__round__(3)} degrees"
#             text_x = center_x - 200
#             text_y = center_y - 80
#             #cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
#             #cv2.putText(image, f"Lower Tip Y-coordinate: {lower_tip_y}", (text_x, text_y + 30), font, font_scale, font_color, font_thickness)

#     # Detecting the blue bounding box
#     yellow_color = np.array([255, 0, 0])
#     color_tolerance = 40
#     color_tolerance2 = 25
#     lower_yellow = yellow_color - color_tolerance
#     upper_yellow = yellow_color + color_tolerance
#     lower_bound_yellow = np.array([139, 139, 192])
#     upper_bound_yellow = lower_bound_yellow + color_tolerance2
#     yellow_mask = cv2.inRange(image, lower_yellow, upper_yellow)
#     yellow_mask2 = cv2.inRange(image, lower_bound_yellow, upper_bound_yellow)
#     contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_yellow2, _ = cv2.findContours(yellow_mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours_yellow:
#         largest_contour2 = max(contours_yellow, key=cv2.contourArea)
#         x, y, w, h = cv2.boundingRect(largest_contour2)
#         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         lower_boundary_y = y + h
#         mid_y = y + h // 4  # Divide into four parts
#         mid2_y = y + (h // 4) * 2  # Second division line
#         mid3_y = y + (h // 4) * 3  # Third division line
#         top_boundary_y = y

#         cv2.line(image, (x, lower_boundary_y), (x + w, lower_boundary_y), (255, 0, 0), 2)
#         cv2.line(image, (x, mid_y), (x + w, mid_y), (0, 0, 255), 2)
#         cv2.line(image, (x, mid2_y), (x + w, mid2_y), (0, 255, 255), 2)  # Draw third line
#         cv2.line(image, (x, mid3_y), (x + w, mid3_y), (255, 255, 0), 2)  # Draw fourth line
#         cv2.line(image, (x, top_boundary_y), (x + w, top_boundary_y), (255, 255, 0), 2)  # Change color for clarity

#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 0.5
#         font_color = (255, 255, 255)
#         font_thickness = 1

#         #text_lower_boundary = f"Lower boundary Y-coordinate: {lower_boundary_y}"
#         #cv2.putText(image, text_lower_boundary, (x, lower_boundary_y + 30), font, font_scale, font_color, font_thickness)

#         #text_mid_line = f"First Division Line Y-coordinate: {mid_y}"
#         #cv2.putText(image, text_mid_line, (x, mid_y + 30), font, font_scale, font_color, font_thickness)

#         #text_mid_line2 = f"Second Division Line Y-coordinate: {mid2_y}"  # Text for second division line
#         #cv2.putText(image, text_mid_line2, (x, mid2_y + 30), font, font_scale, font_color, font_thickness)

#         #text_mid_line3 = f"Third Division Line Y-coordinate: {mid3_y}"  # Text for third division line
#         #cv2.putText(image, text_mid_line3, (x, mid3_y + 30), font, font_scale, font_color, font_thickness)

#         #text_top_boundary = f"Top boundary Y-coordinate: {top_boundary_y}"
#         #cv2.putText(image, text_top_boundary, (x, top_boundary_y + 30), font, font_scale, font_color, font_thickness)

#         # Comparing y-coordinate of red object with bounding box
#         if lower_tip_y < lower_boundary_y and lower_tip_y > mid3_y:
#             recommendation = "Left side: good level"
#         elif lower_tip_y < lower_boundary_y and lower_tip_y > mid2_y:
#             recommendation = "Left side: average level"
#         elif lower_tip_y < mid_y:
#             recommendation = "Left side: severe impaction"
#         else:
#             recommendation = "No Impaction"

#         cv2.putText(image, recommendation, (30, 70), font, 1, (0, 255, 0), 2)

#     if not contours_yellow and not contours_yellow2:
#         print("Neighbouring tooth is not found in the image.")

#     #######END OF LEFT SIDE#####################

#     #START OF RIGHT SIDE

#     pink_color = np.array([255, 0, 255])  # BGR format
#     color_tolerance = 40
#     lower_red = pink_color - color_tolerance
#     upper_red = pink_color + color_tolerance
#     mask = cv2.inRange(image, lower_red, upper_red)
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours:
#         largest_contour2 = max(contours, key=cv2.contourArea)
#         if largest_contour2.size > 10:
#             ellipse2 = cv2.fitEllipse(largest_contour2)
#             angle = 180 - ellipse2[2]
#             center_x, center_y = map(int, ellipse2[0])
#             cv2.ellipse(image, ellipse2, (0, 255, 0), 2)
#             main_axis_length = int(ellipse2[1][1] / 2)
#             x_main = int(ellipse2[0][0] - main_axis_length * np.sin(np.radians(ellipse2[2])))
#             y_main = int(ellipse2[0][1] + main_axis_length * np.cos(np.radians(ellipse2[2])))

#             cv2.line(image, (int(ellipse2[0][0] + main_axis_length * np.sin(np.radians(ellipse2[2]))),
#                             int(ellipse2[0][1] - main_axis_length * np.cos(np.radians(ellipse2[2])))),
#                     (x_main, y_main), (0, 0, 0), 2)

#             lower_tip_y2 = max(ellipse2[0][1], y_main)


#             font = cv2.FONT_HERSHEY_SIMPLEX
#             font_scale = 0.7
#             font_color = (0, 0, 0)
#             font_thickness = 2
#             #angle_text = f"Angle: {angle.__round__(3)} degrees"
#             text_x = center_x - 200
#             text_y = center_y - 80
#             #cv2.putText(image, angle_text, (text_x, text_y), font, font_scale, font_color, font_thickness)
#             #cv2.putText(image, f"Lower Tip Y-coordinate: {lower_tip_y2}", (text_x, text_y + 30), font, font_scale, font_color, font_thickness)

#     # Detecting the baby blue/ light blue bounding box
#     babyBlue_color = np.array([255, 255, 0])
#     color_tolerance = 40
#     color_tolerance2 = 25
#     lower_yellow = babyBlue_color - color_tolerance
#     upper_yellow = babyBlue_color + color_tolerance
#     lower_bound_yellow = np.array([139, 139, 192])
#     upper_bound_yellow = lower_bound_yellow + color_tolerance2
#     yellow_mask = cv2.inRange(image, lower_yellow, upper_yellow)
#     yellow_mask2 = cv2.inRange(image, lower_bound_yellow, upper_bound_yellow)
#     contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_yellow2, _ = cv2.findContours(yellow_mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours_yellow:
#         largest_contour2 = max(contours_yellow, key=cv2.contourArea)
#         x, y, w, h = cv2.boundingRect(largest_contour2)
#         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         lower_boundary_yy = y + h
#         mid_yy = y + h // 4  # Divide into four parts
#         mid2_yy = y + (h // 4) * 2  # Second division line
#         mid3_yy = y + (h // 4) * 3  # Third division line
#         top_boundary_yy = y

#         cv2.line(image, (x, lower_boundary_yy), (x + w, lower_boundary_yy), (255, 0, 0), 2)
#         cv2.line(image, (x, mid_yy), (x + w, mid_yy), (0, 0, 255), 2)
#         cv2.line(image, (x, mid2_yy), (x + w, mid2_yy), (0, 255, 255), 2)  # Draw third line
#         cv2.line(image, (x, mid3_yy), (x + w, mid3_yy), (255, 255, 0), 2)  # Draw fourth line
#         cv2.line(image, (x, top_boundary_yy), (x + w, top_boundary_yy), (255, 255, 0), 2)  # Change color for clarity

#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 0.5
#         font_color = (255, 255, 255)
#         font_thickness = 1

#         # text_lower_boundary = f"Lower boundary: {lower_boundary_yy}"
#         # cv2.putText(image, text_lower_boundary, (x, lower_boundary_yy + 30), font, font_scale, font_color, font_thickness)

#         # text_mid_line = f"First Div: {mid_yy}"
#         # cv2.putText(image, text_mid_line, (x, mid_yy + 30), font, font_scale, font_color, font_thickness)

#         # text_mid_line2 = f"Second Div: {mid2_yy}"  # Text for second division line
#         # cv2.putText(image, text_mid_line2, (x, mid2_yy + 30), font, font_scale, font_color, font_thickness)

#         # text_mid_line3 = f"Third Div: {mid3_yy}"  # Text for third division line
#         # cv2.putText(image, text_mid_line3, (x, mid3_yy + 30), font, font_scale, font_color, font_thickness)

#         # text_top_boundary = f"Top boundary: {top_boundary_yy}"
#         # cv2.putText(image, text_top_boundary, (x, top_boundary_yy + 30), font, font_scale, font_color, font_thickness)

#         # Comparing y-coordinate of red object with bounding box
#         if lower_tip_y2 < lower_boundary_yy and lower_tip_y2 > mid3_yy:
#             recommendation = "Right side: good level"
#         elif lower_tip_y2 < lower_tip_y2 and lower_tip_y2 > mid2_yy:
#             recommendation = "Right side:  average level"
#         elif lower_tip_y2 < mid_yy:
#             recommendation = "Right side: poor level"
#         else:
#             recommendation = "No Impaction"

#         cv2.putText(image, recommendation, (10, 30), font, 1, (0, 255, 0), 2)

#     if not contours_yellow and not contours_yellow2:
#         print("Neighbouring tooth is not found in the image.")
#     # Display the image with the detected object
#     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     plt.show()


#     # Save the image
#     cv2.imwrite('angulation_and_4_parts_bounding_box_with_recommendation.jpg', image)
#     fig, ax = plt.subplots()
#     ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     ax.axis('off')  # this will hide the x-axis and y-axis
#     st.write("Please find the Vertical Height below:")
#     st.pyplot(fig)  # display the matplotlib plot in Streamlit

#     #Overlap
#     image =original_image.copy()
#     def find_tip_of_Left_canine(contours):
#         tip_x = None
#         if contours:
#             cv2.drawContours(image, contours, -1, (0, 255, 0), 1)
#             # Find the contour with the leftmost point
#             leftmost_points = [tuple(c[c[:, :, 0].argmin()][0]) for c in contours if c.shape[0] > 5]
#             if leftmost_points:
#                 # Find the leftmost point among all contours
#                 leftmost = min(leftmost_points, key=lambda point: point[0])
#                 tip_x = leftmost[0]
#                 cv2.circle(image, leftmost, 5, (0, 0, 255), -1)  # Red circle for the tip
#         return tip_x

#     def find_tip_of_Right_canine(contours):
#         tip_x = None
#         if contours:
#             cv2.drawContours(image, contours, -1, (0, 255, 0), 1)
#             # Find the contour with the rightmost point
#             rightmost_points = [tuple(c[c[:, :, 0].argmax()][0]) for c in contours if c.shape[0] > 5]
#             if rightmost_points:
#                 # Find the rightmost point among all contours
#                 rightmost = max(rightmost_points, key=lambda point: point[0])
#                 tip_x = rightmost[0]
#                 cv2.circle(image, rightmost, 5, (0, 0, 255), -1)  # Red circle for the tip
#         return tip_x

#     def find_leftmost_of_Left_canine(contours):
#         if contours:
#             largest_contour = max(contours, key=cv2.contourArea)
#             leftmost_x = max(c[c[:, :, 0].argmin()][0][0] for c in contours)
#             return leftmost_x
#         return None


#     def find_rightmost_of_Right_canine(contours):
#         if contours:
#             largest_contour = max(contours, key=cv2.contourArea)  # Find the largest contour based on area
#             rightmost_x = max(c[c[:, :, 0].argmax()][0][0] for c in contours)  # Find the rightmost x-coordinate
#             return rightmost_x
#         return None

#     def find_rightmost_of_Left_incisor(contours):
#         if contours:
#             largest_contour = max(contours, key=cv2.contourArea)
#             x, y, w, h = cv2.boundingRect(largest_contour)
#             rightmost_x = min(c[c[:, :, 0].argmin()][0][0] for c in contours)  # Rightmost boundary of the incisor
#             return rightmost_x
#         return None

#     def find_leftmost_of_Right_incisor(contours):
#         if contours:
#             largest_contour = max(contours, key=cv2.contourArea)
#             x, y, w, h = cv2.boundingRect(largest_contour)
#             leftmost_x = min(c[c[:, :, 0].argmin()][0][0] for c in contours)
#             return leftmost_x
#         return None

#     # Convert the image to HSV format
#     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#     # Define the range for blue color in HSV
#     lower_blue = np.array([110, 50, 50])
#     upper_blue = np.array([130, 255, 255])
#     blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
#     blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Define the range for green color in HSV
#     lower_green = np.array([50, 50, 50])
#     upper_green = np.array([70, 255, 255])
#     green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
#     green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     #pink
#     pink_lower = np.array([140, 100, 100])
#     pink_upper = np.array([160, 255, 255])
#     pink_mask = cv2.inRange(hsv_image, pink_lower, pink_upper)
#     pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     #cyan
#     cyan_lower = np.array([85, 100, 100])
#     cyan_upper = np.array([95, 255, 255])
#     cyan_mask = cv2.inRange(hsv_image, cyan_lower, cyan_upper)
#     cyan_contours, _ = cv2.findContours(cyan_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


#     # blue contours
#     for contour in blue_contours:
#         if cv2.contourArea(contour) > 100:  # Filter out small contours
#             ellipse = cv2.fitEllipse(contour)
#             cv2.ellipse(image, ellipse, (255, 0, 0), 2)  # Blue ellipse
#             Left_center_x, Left_center_y = map(int, ellipse[0])

#             # Calculate the endpoints for the main axis of the ellipse
#             Left_main_axis_length = int(ellipse[1][1] / 2)  # Half the length of the minor axis
#             Left_x_main = int(Left_center_x - Left_main_axis_length * np.sin(np.radians(ellipse[2])))
#             Left_y_main = int(Left_center_y + Left_main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(image, (int(Left_center_x + Left_main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(Left_center_y - Left_main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (Left_x_main, Left_y_main), (0, 255, 0), 2)  # Green line for blue ellipse

#             leftmost_x_Left_canine = find_leftmost_of_Left_canine(green_contours)
#             Left_canine_tip_x = find_tip_of_Left_canine(green_contours)
#             if Left_canine_tip_x is not None:
#                 if Left_canine_tip_x >= Left_center_x:
#                     print("The condition of the left canine's position is good")
#                     overL = "Good"
#                 elif Left_center_x > Left_canine_tip_x >= (Left_center_x + Left_main_axis_length):
#                     print("The condition of the left canine's position is Average")
#                     overL = "Average"
#                 else:
#                     print("The condition of the left canine's position is poor")
#                     overL = "Poor"
#             else :
#                 print("Unable to detect the left canine")


#     # cyan contours
#     for contour in cyan_contours:
#         if cv2.contourArea(contour) > 100:  # Filter out small contours
#             ellipse = cv2.fitEllipse(contour)
#             cv2.ellipse(image, ellipse, (255, 0, 0), 2)  # Blue ellipse
#             Right_center_x, Right_center_y = map(int, ellipse[0])

#             # Calculate the endpoints for the main axis of the ellipse
#             Right_main_axis_length = int(ellipse[1][1] / 2)  # Half the length of the minor axis
#             Right_x_main = int(Right_center_x - Right_main_axis_length * np.sin(np.radians(ellipse[2])))
#             Right_y_main = int(Right_center_y + Right_main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(image, (int(Right_center_x + Right_main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(Right_center_y - Right_main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (Right_x_main, Right_y_main), (0, 255, 0), 2)  # Green line for blue ellipse

#             Rightmost_x_Right_canine = find_rightmost_of_Right_canine(pink_contours)
#             Right_canine_tip_x = find_tip_of_Right_canine(pink_contours)
#             if Right_canine_tip_x is not None:
#                 if Right_canine_tip_x <= Right_center_x:
#                     print("The condition of the right canine's position is good")
#                     overR = "Good"
#                 elif Right_center_x < Right_canine_tip_x <= (Right_center_x + Right_main_axis_length):
#                     print("The condition of the right canine's position is Average")
#                     overR = "Average"
#                 else:
#                     print("The condition of the right canine's position is poor")
#                     overR = "Poor"
#             else :
#                 print("Unable to detect the right canine")



#     if Left_canine_tip_x is None and Right_canine_tip_x is None:
#         print("No Detection")
#     else :
#     # Display the image using Matplotlib's imshow function
#         plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         plt.axis('off') # this will hide the x-axis and y-axis
#         plt.show()
#         # save the image
#         cv2.imwrite('overlap.jpg', image)
#         fig, ax = plt.subplots()
#         ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         ax.axis('off')  # this will hide the x-axis and y-axis
#         st.write("Please find the Overlap below:")
#         st.pyplot(fig)  # display the matplotlib plot in Streamlit
#     #Apex Position

#     # Load the image
#     input_image = original_image.copy()

#     L_first_premolar = np.array([0, 0, 255])  # BGR format
#     L_second_premolar = np.array([0, 255, 255])  # BGR format
#     L_canine = np.array([0, 255, 0])  # BGR format


#     R_first_premolar = np.array([128, 0, 128])  # BGR format
#     R_second_premolar = np.array([0, 165, 255])  # BGR format
#     R_canine = np.array([255, 0, 255])  # BGR format

#     # Define the tolerance range for the color (adjustable)
#     color_tolerance = 40
#     color_tolerance2 = 25

#     # Define lower and upper bounds for the color with tolerance
#     lower_R_Canine = R_canine - color_tolerance
#     upper_R_Canine = R_canine + color_tolerance
#     lower_R_first = R_first_premolar - color_tolerance
#     upper_R_first = R_first_premolar + color_tolerance
#     lower_R_second = R_second_premolar - color_tolerance2
#     upper_R_second = R_second_premolar + color_tolerance2
#     mask_R_Canine= cv2.inRange(input_image, lower_R_Canine, upper_R_Canine)
#     mask_R_first= cv2.inRange(input_image, lower_R_first, upper_R_first)
#     mask_R_second= cv2.inRange(input_image, lower_R_second, upper_R_second)
#     # Find contours in the masked image
#     contours_R_Canine, _ = cv2.findContours(mask_R_Canine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_R_first, _ = cv2.findContours(mask_R_first, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_R_second, _ = cv2.findContours(mask_R_second, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


#     lower_L_Canine = L_canine - color_tolerance
#     upper_L_Canine = L_canine + color_tolerance
#     lower_L_first = L_first_premolar - color_tolerance
#     upper_L_first = L_first_premolar + color_tolerance
#     lower_L_second = L_second_premolar - color_tolerance2
#     upper_L_second = L_second_premolar + color_tolerance2
#     mask_L_Canine= cv2.inRange(input_image, lower_L_Canine, upper_L_Canine)
#     mask_L_first= cv2.inRange(input_image, lower_L_first, upper_L_first)
#     mask_L_second= cv2.inRange(input_image, lower_L_second, upper_L_second)
#     # Find contours in the masked image
#     contours_L_Canine, _ = cv2.findContours(mask_L_Canine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_L_first, _ = cv2.findContours(mask_L_first, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_L_second, _ = cv2.findContours(mask_L_second, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     L_x_first = 0
#     L_w_first = 0
#     L_x_second = 0
#     L_w_second = 0

#     R_x_first = 0
#     R_w_first = 0
#     R_x_second = 0
#     R_w_second = 0

#     L_apex_position = 0
#     R_apex_position = 0

#     if contours_L_Canine:
#         # Get the largest contour
#         largest_contour = max(contours_L_Canine, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # Extract the angle of inclination from the fitted ellipse
#             angle = ellipse[2]

#             # Display the angle
#             print(f"Angle of inclination left canine: {angle} degrees")
#             center_x, center_y = map(int, ellipse[0])

#             # Calculate the endpoints for the main axis of the ellipse
#             main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
#             x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
#             y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(input_image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (x_main, y_main), (255, 0, 0), 2)

#             L_apex_position = int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2])))

#     if contours_R_Canine:
#         # Get the largest contour
#         largest_contour = max(contours_R_Canine, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # Extract the angle of inclination from the fitted ellipse
#             angle = ellipse[2]

#             # Display the angle
#             print(f"Angle of inclination right canine: {angle} degrees")
#             center_x, center_y = map(int, ellipse[0])

#             # Calculate the endpoints for the main axis of the ellipse
#             main_axis_length = int(ellipse[1][1] / 2)  # Half the length of minor axis
#             x_main = int(ellipse[0][0] - main_axis_length * np.sin(np.radians(ellipse[2])))
#             y_main = int(ellipse[0][1] + main_axis_length * np.cos(np.radians(ellipse[2])))

#             # Draw the main axis of the ellipse
#             cv2.line(input_image, (int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2]))),
#                             int(ellipse[0][1] - main_axis_length * np.cos(np.radians(ellipse[2])))),
#                     (x_main, y_main), (255, 0, 0), 2)

#             R_apex_position = int(ellipse[0][0] + main_axis_length * np.sin(np.radians(ellipse[2])))

#     if contours_L_first:
#         # Get the largest contour
#         largest_contour = max(contours_L_first, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)
#             # Draw the ellipse on the original image
#             # cv2.ellipse(first_img, ellipse, (0, 255, 0), 2)
#             L_x_first, y, L_w_first, h = cv2.boundingRect(largest_contour)

#         if  h > 10:  # Adjust the minimum width and height as needed
#             # Draw the rectangle on the original image
#             img1_height = input_image.shape[0]
#             #cv2.rectangle(input_image, (x_first, 0), (x_first + w_first, img1_height), (0, 255, 255), 2)

#     if contours_R_first:
#         # Get the largest contour
#         largest_contour = max(contours_R_first, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)
#             # Draw the ellipse on the original image
#             # cv2.ellipse(first_img, ellipse, (0, 255, 0), 2)
#             R_x_first, y, R_w_first, h = cv2.boundingRect(largest_contour)

#         if  h > 10:  # Adjust the minimum width and height as needed
#             # Draw the rectangle on the original image
#             img1_height = input_image.shape[0]
#             #cv2.rectangle(input_image, (x_first, 0), (x_first + w_first, img1_height), (0, 255, 255), 2)

#     if contours_L_second:
#         # Get the largest contour
#         largest_contour = max(contours_L_second, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # # Draw the ellipse on the original image
#             # cv2.ellipse(second_img, ellipse, (0, 255, 0), 2)

#             L_x_second, y, L_w_second, h = cv2.boundingRect(largest_contour)

#             if h > 10:  # Adjust the minimum width and height as needed
#                 # Draw the rectangle on the original image
#                 img2_height = input_image.shape[0]

#                 #cv2.rectangle(input_image, (x_second, 0), (x_second + w_second, img2_height), (0, 0, 255), 2)

#     if contours_R_second:
#         # Get the largest contour
#         largest_contour = max(contours_R_second, key=cv2.contourArea)
#         # Fit an ellipse to the contour
#         if largest_contour.size > 10:

#             ellipse = cv2.fitEllipse(largest_contour)

#             # # Draw the ellipse on the original image
#             # cv2.ellipse(second_img, ellipse, (0, 255, 0), 2)

#             R_x_second, y, R_w_second, h = cv2.boundingRect(largest_contour)

#             if h > 10:  # Adjust the minimum width and height as needed
#                 # Draw the rectangle on the original image
#                 img2_height = input_image.shape[0]

#                 #cv2.rectangle(input_image, (x_second, 0), (x_second + w_second, img2_height), (0, 0, 255), 2)

#     overlay = input_image.copy()

#     if contours_L_first and contours_L_second:
#         img_height = input_image.shape[0]

#         # Create a transparent overlay
#         # overlay = input_image.copy()

#         # Calculate coordinates for the first rectangle
#         L_x_first, y_first, L_w_first, h_first = cv2.boundingRect(max(contours_L_first, key=cv2.contourArea))
#         L_line3 = int((L_x_first + L_w_first + L_x_second) / 2)
#         L_line2 = L_x_first
#         # Draw the first rectangle on the overlay with opacity 0.2
#         rect1_points = np.array([[L_x_first, 0], [L_line3, 0], [L_line3, img_height], [L_x_first, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [rect1_points], color=(0, 255, 255), lineType=cv2.LINE_AA)

#         # Calculate coordinates for the second rectangle
#         x_second, y_second, w_second, h_second = cv2.boundingRect(max(contours_L_second, key=cv2.contourArea))
#         line4 = L_line3 + w_second
#         # Draw the second rectangle on the overlay with opacity 0.3
#         rect2_points = np.array([[L_line3, 0], [L_line3 + w_second, 0], [L_line3 + w_second, img_height], [L_line3, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [rect2_points], color=(0, 0, 255), lineType=cv2.LINE_AA)

#         # Print and draw the green zone
#         yellow_zone = int(L_line3 - L_x_first)
#         red_zone = int(w_second)
#         green_zone = int((yellow_zone + red_zone) / 2)
#         print(L_x_first, x_second, red_zone, yellow_zone, green_zone)

#         # Draw the green zone rectangle on the overlay with opacity 0.3
#         line1 = L_x_first - green_zone
#         green_rect_points = np.array([[L_x_first - green_zone, 0], [L_x_first, 0], [L_x_first, img_height], [L_x_first - green_zone, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [green_rect_points], color=(0, 255, 0), lineType=cv2.LINE_AA)

#         # Blend the overlay with the original image using cv2.addWeighted
#         # opacity = 0.2
#         # image_output = cv2.addWeighted(input_image, 1 - opacity, overlay, opacity, 0)

#         if L_apex_position > L_line3:
#             apexL = "Poor"
#         elif L_apex_position > L_line2:
#             apexL = "Average"
#         else:
#             apexL = "Good"

#     if contours_R_first and contours_R_second:
#         img_height = input_image.shape[0]

#         # Create a transparent overlay
#         # overlay = input_image.copy()

#         # Calculate coordinates for the first rectangle
#         R_x_first, y_first, R_w_first, h_first = cv2.boundingRect(max(contours_R_first, key=cv2.contourArea))
#         R_line3 = int((R_x_second + R_w_second + R_x_first) / 2)
#         R_line2 = R_x_first + R_w_first
#         # Draw the first rectangle on the overlay with opacity 0.2
#         rect1_points = np.array([[R_line2, 0], [R_line3, 0], [R_line3, img_height], [R_line2, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [rect1_points], color=(0, 255, 255), lineType=cv2.LINE_AA)

#         # Calculate coordinates for the second rectangle
#         x_second, y_second, w_second, h_second = cv2.boundingRect(max(contours_R_second, key=cv2.contourArea))
#         line4 = R_line3 - w_second
#         # Draw the second rectangle on the overlay with opacity 0.3
#         rect2_points = np.array([[R_line3, 0], [R_line3 - w_second, 0], [R_line3 - w_second, img_height], [R_line3, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [rect2_points], color=(0, 0, 255), lineType=cv2.LINE_AA)

#         # Print and draw the green zone
#         yellow_zone = int(R_line2 - R_line3)
#         red_zone = int(w_second)
#         green_zone = int((yellow_zone + red_zone) / 2)
#         # print(R_x_first, x_second, red_zone, yellow_zone, green_zone)
#         # print(R_line3, R_line2)

#         # Draw the green zone rectangle on the overlay with opacity 0.3
#         line1 = R_line2 + green_zone
#         green_rect_points = np.array([[line1, 0], [R_line2, 0], [R_line2, img_height], [line1, img_height]], dtype=np.int32)
#         cv2.fillPoly(overlay, [green_rect_points], color=(0, 255, 0), lineType=cv2.LINE_AA)

#         if R_apex_position < R_line3:
#             apexR = "Poor"
#         elif R_apex_position < R_line2:
#             apexR = "Average"
#         else:
#             apexR = "Good"

#     opacity = 0.2
#     # image_output = cv2.addWeighted(input_image, 1 - opacity, overlay_L, opacity, 0)
#     image_output = cv2.addWeighted(input_image, 1 - opacity, overlay, opacity, 0)
#     if not contours_L_first and not contours_L_second:
#         print("left canine: No premolars object found in the image.")
#     elif not contours_R_first and not contours_R_second:
#         print("right canine: No premolars object found in the image.")
#     else:
#         plt.imshow(cv2.cvtColor(image_output, cv2.COLOR_BGR2RGB))
#         plt.axis('off') # this will hide the x-axis and y-axis
#         plt.show()
#         cv2.imwrite('apex_position.jpg', image_output)
#         fig, ax = plt.subplots()
#         ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         ax.axis('off')  # this will hide the x-axis and y-axis
#         st.write("Please find the Apex Position below:")
#         st.pyplot(fig)  # display the matplotlib plot in Streamlit

#     #Recommandation
#     def recomend(angle,apex,vertical,over):
#         #All 4 Good
#         if angle=="Good" and apex=="Good" and vertical=="Good" and over=="Good":
#             print("Straight Forward Impaction")
#         #Apex Position Average
#         elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Good":
#             print("Mildly Difficult Impaction")
#         #Apex Position Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Good" and over=="Good":
#             print("Mildly Difficult Impaction")


#         #overlap Average
#         elif angle=="Good" and apex=="Good" and vertical=="Good" and over=="Average":
#             print("Mildly Difficult Impaction")
#         #overlap  and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Average":
#             print("Mildly Difficult Impaction")
#         #overlap Average and Apex Poor
#         elif angle=="Good" and apex=="poor" and vertical=="Good" and over=="Average":
#             print("Moderately Difficult Impaction")


#         #overlap poor
#         elif angle=="Good" and apex=="Good" and vertical=="Good" and over=="Poor":
#             print("Mildly Difficult Impaction")
#         #overlap poor and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Good" and over=="Poor":
#             print("Moderately Difficult Impaction")
#         #overlap poor and Apex Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Good" and over=="Poor":
#             print("Moderately Difficult Impaction")


#         #Vertical Height Average
#         elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Good":
#             print("Moderately Difficult Impaction")
#         #Vertical Height and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Good":
#             print("Moderately Difficult Impaction")
#         #Vertical Height Average and Apex poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Good":
#             print("Moderately Difficult Impaction")


#         #Vertical Height and Overlap Average
#         elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Averge":
#             print("Moderately Difficult Impaction")
#         #Vertical Height and Apex and Overlap Average
#         elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Average":
#             print("Moderately Difficult Impaction")
#         #Vertical Height and Overlap Average and  Apex Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")


#         #Vertical Height Average and Overlap Poor
#         elif angle=="Good" and apex=="Good" and vertical=="Average" and over=="Poor":
#             print("Moderately Difficult Impaction")
#         #Vertical Height and Apex Average and Overlap Poor
#         elif angle=="Good" and apex=="Average" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")
#         #Vertical Height Average and Apex and Overlap Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")


#         #Vertical Height Poor
#         elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Good":
#             print("Difficult Impaction")
#         #Vertical Height Poor and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Good":
#             print("Difficult Impaction")
#         #Vertical Height Poor and Apex Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Good":
#             print("Difficult Impaction")

#         #Vertical Height Poor and overlap average
#         elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Average":
#             print("Difficult Impaction")
#         #Vertical Height Poor and overlap average and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Average":
#             print("Difficult Impaction")
#         #Vertical Height Poor and overlap average and Apex Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Average":
#             print("Difficult Impaction")

#         #Vertical Height Poor and overlap poor
#         elif angle=="Good" and apex=="Good" and vertical=="Poor" and over=="Poor":
#             print("Difficult Impaction")
#         #Vertical Height Poor and overlap poor and Apex Average
#         elif angle=="Good" and apex=="Average" and vertical=="Poor" and over=="Poor":
#             print("Difficult Impaction")
#         #Vertical Height Poor and overlap poor and Apex Poor
#         elif angle=="Good" and apex=="Poor" and vertical=="Poor" and over=="Poor":
#             print("Difficult Impaction")


#         #angle average
#         elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Good":
#             print("Moderately Difficult Impaction")
#         #angle average apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Good":
#             print("Moderately Difficult Impaction")
#         #angle average and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Good":
#             print("Moderately Difficult Impaction")


#         #angle average and overlap averge
#         elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Average":
#             print("Moderately Difficult Impaction")
#         ##angle average and overlap averge  apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Average":
#             print("Moderately Difficult Impaction")
#         ##angle average and overlap averge  and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Average":
#             print("Difficult Impaction")


#         #angle average and overlap poor
#         elif angle=="Average" and apex=="Good" and vertical=="Good" and over=="Poor":
#             print("Moderately Difficult Impaction")
#         ##angle average and overlap poor  apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Good" and over=="Poor":
#             print("Difficult Impaction")
#         ##angle average and overlap poor  and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Good" and over=="Poor":
#             print("Difficult Impaction")


#         #angle average and vetical average
#         elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")
#         #angle average and vetical average apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")
#         #angle average and vetical average and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")


#         #angle average and vetical and overlap average
#         elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")
#         #angle average and vetical and overlap average apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")
#         #angle average and vetical and overlap average and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")


#         #angle average and vetical average and overlap poor
#         elif angle=="Average" and apex=="Good" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")
#         #angle average and vetical average apex average and overlap poor
#         elif angle=="Average" and apex=="Average" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")
#         #angle average and vetical average and apex poor and overlap poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")


#         #angle average and vetical poor
#         elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Good":
#             print("Difficult Impaction")
#         #angle average and vetical poor apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Poor"  and over=="Good":
#             print("Difficult Impaction")
#         #angle average and vetical poor and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Poor"  and over=="Good":
#             print("Difficult Impaction")


#         #angle average and vetical poor and overlap average
#         elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Average":
#             print("Difficult Impaction")
#         #angle average and veticalpoor and overlap average apex average
#         elif angle=="Average" and apex=="Average" and vertical=="Poor" and over=="Average":
#             print("Difficult Impaction")
#         #angle average and vetical poor and overlap average and apex poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Poor" and over=="Average":
#             print("Complicated Impaction")


#         #angle average and vetical poor and overlap poor
#         elif angle=="Average" and apex=="Good" and vertical=="Poor" and over=="Poor":
#             print("Difficult Impaction")
#         #angle average and vetical poor apex average and overlap poor
#         elif angle=="Average" and apex=="Average" and vertical=="Poor" and over=="Poor":
#             print("Complicated Impaction")
#         #angle average and vetical poor and apex poor and overlap poor
#         elif angle=="Average" and apex=="Poor" and vertical=="Poor" and over=="Poor":
#             print("Complicated Impaction")


#         #angle poor
#         elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Good":
#             print("Difficult Impaction")
#         #angle poor apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Good":
#             print("Difficult Impaction")
#         #angle poor and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Good":
#             print("Difficult Impaction")


#         #angle poor and overlap average
#         elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Average":
#             print("Difficult Impaction")
#         #angle poor and overlap average and apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Average":
#             print("Difficult Impaction")
#         #angle poor and overlap average and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Average":
#             print("Difficult Impaction")


#         #angle poor and overlap poor
#         elif angle=="Poor" and apex=="Good" and vertical=="Good" and over=="Poor":
#             print("Difficult Impaction")
#         #angle poor and overlap poor and apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Good" and over=="Poor":
#             print("Difficult Impaction")
#         #angle poor and overlap poor and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Good" and over=="Poor":
#             print("Difficult Impaction")


#         #angle poor and vertical average
#         elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")
#         #angle poor and vertical average apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")
#         #angle poor and vertical average and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Good":
#             print("Difficult Impaction")


#         #angle poor and vertical average and over average
#         elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")
#         #angle poor and vertical average and over average apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Average":
#             print("Difficult Impaction")
#         #angle poor and vertical average and over average and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Average":
#             print("Complicated Impaction")


#         #angle poor and vertical average and over poor
#         elif angle=="Poor" and apex=="Good" and vertical=="Average" and over=="Poor":
#             print("Difficult Impaction")
#         #angle poor and vertical average and over poor apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Average" and over=="Poor":
#             print("Complicated Impaction")
#         #angle poor and vertical average and over poor and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Average" and over=="Poor":
#             print("Complicated Impaction")


#         #angle poor and vertical poor
#         elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Good":
#             print("Complicated Impaction")
#         #angle poor and vertical poor and apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Good":
#             print("Complicated Impaction")
#         #angle poor and vertical poor and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Good":
#             print("Complicated Impaction")


#         #angle poor and vertical poor and over average
#         elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Average":
#             print("Complicated Impaction")
#         #angle poor and vertical average and over average apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Average":
#             print("Complicated Impaction")
#         #angle poor and vertical average and over average and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Average":
#             print("Complicated Impaction")


#         #angle poor and vertical poor and over poor
#         elif angle=="Poor" and apex=="Good" and vertical=="Poor" and over=="Poor":
#             print("Complicated Impaction")
#         #angle poor and vertical poor and over poor apex average
#         elif angle=="Poor" and apex=="Average" and vertical=="Poor" and over=="Poor":
#             print("Complicated Impaction")
#         #angle poor and vertical poor and over poor and apex poor
#         elif angle=="Poor" and apex=="Poor" and vertical=="Poor" and over=="Poor":
#             print("Very Complicated Impaction")

#     print("Left Canine: ")
#     print("Angulation : {} ,Vertical Height : {} , OverLap : {} , Apex Position : {} ".format(angleL,verticalL,overL,apexL))
#     print("Recomendation :" )
#     recomend(angleL,apexL,verticalL,overL)

#     print("Right Canine : ")
#     print("Angulation : {} , Vertical Height : {} , OverLap : {} , Apex Position : {}".format(angleR,verticalR,overR,apexR))
#     print("Recomendation :" )
#     recomend(angleR,apexR,verticalR,overR)

