import os
import shapefile
from bs4 import BeautifulSoup

# Config

SOURCE_PATH = './svg/'  # default source path
TARGET_PATH = './shp/'  # default source path

NW_X = '0'
NW_Y = '0'

# Methods


def get_proper_path(path: str) -> str:
    '''
    Used for preparion path to directory.
    '''
    return path.replace('/', os.sep).replace('\\', os.sep).rstrip(os.sep) + os.sep


def get_geometry(data_str: str) -> list:
    '''
    Getting and preparing for shapefile coordinates list from svg-path attribute 'd'.
    '''
    geom = list()
    parts = data_str.split('m')
    parts.pop(0)
    for part in parts:
        if part.strip()[-1] == 'z':
            flag = True
        else:
            flag = False
        geom_part = part. \
            replace('z', '').\
            replace('l', '').\
            strip().\
            split()
        if len(geom_part) % 2 != 0:
            raise ValueError('ERROR: Object geometry is broken.')
        geom.append([[float(geom_part[i]), float(geom_part[i+1]) * -1]
                     for i in range(0, len(geom_part), 2)])
        if flag and geom[0][0] != geom[-1][0] and geom[0][1] != geom[-1][1]:
            geom.append(geom[0])
    return geom


# Script
print('Check README.md to avoid any problems or questions.')

source_dir = input(
    f'Enter the folder, contaiing svg-files [{SOURCE_PATH}]: ')
target_dir = input(
    f'Enter the folder for shp-files [{TARGET_PATH}]: ')
print('')

source_dir = get_proper_path(
    SOURCE_PATH) if source_dir == '' else get_proper_path(source_dir)
target_dir = get_proper_path(
    TARGET_PATH) if target_dir == '' else get_proper_path(target_dir)

if not os.path.isdir(source_dir):
    raise ValueError('ERROR: Source folder not found.')
if not os.path.isdir(target_dir):
    raise ValueError('ERROR: Target folder not found.')
if len(os.listdir(target_dir)) > 0:
    flag = False
    while not flag:
        print(
            'Target folder is not empty. Current files may be overwritten. Continue? [y/N]: ', end='')
        answer = input()
        if answer == '' or answer.lower() == 'n' or answer.lower() == 'no':
            raise ValueError('ERROR: target folder is not empty.')
        elif answer.lower() == 'y' or answer.lower() == 'yes':
            flag = True
        else:
            print('Can not continue until get a correct answer.')

source_files = [file_name for file_name in os.listdir(source_dir) if
                any(file_name.lower().endswith(ext) for ext in ['svg'])]

if len(source_files) == 0:
    raise ValueError('ERROR: SVG files not found in source directory.')

area_objs, area_attr, line_objs, line_attr = ([] for _ in range(4))
line_types_ignore = ['h', 'v', 'c', 'q', 's', 'q', 't', 'a']

raise_warning_type_one = False
raise_warning_type_two = False

for svg_file in source_files:
    soup = BeautifulSoup(open(source_dir + svg_file), features='xml')
    draws = soup.select('path')
    for draw in draws:
        if draw.parent.name.lower() == 'clippath':
            flag = False
        else:
            flag = True
        if draw.has_attr('d') and flag:
            data_str = draw['d'].lower().strip()
            flag = True
            for l_type in line_types_ignore:
                if l_type in data_str:
                    flag = False
            if flag \
                    and draw.has_attr('fill') \
                    and draw['fill'].lower() != 'none' \
                    and data_str[-1] == 'z':
                # poly
                area_objs.append(get_geometry(data_str))
                area_attr.append(draw['fill'])
            elif flag:
                # line
                line_objs.append(get_geometry(data_str))
                if draw.has_attr('stroke') and draw['stroke'].lower() != 'none':
                    line_attr.append(draw['stroke'])
                elif draw.parent.has_attr('stroke') and draw.parent['stroke'].lower() != 'none':
                    line_attr.append(draw.parent['stroke'])
                else:
                    line_attr.append(None)
            else:
                if not raise_warning_type_one:
                    print(
                        'WARNING: unsupported line types is deteted. Ignoring such objects.')
                    raise_warning_type_one = True
        else:
            if not raise_warning_type_two:
                print('WARNING: no geometry found. Ignoring such objects.')
                raise_warning_type_two = True
    a_shp_file = shapefile.Writer(
        target_dir + 'a_' + svg_file[:-4], shapeType=shapefile.POLYGON)
    a_shp_file.field('fill', 'C', size=255)
    l_shp_file = shapefile.Writer(
        target_dir + 'l_' + svg_file[:-4], shapeType=shapefile.POLYLINE)
    l_shp_file.field('stroke', 'C', size=255)

    for i in range(len(area_objs)):
        a_shp_file.poly(area_objs[i])
        a_shp_file.record(area_attr[i])
    for i in range(len(line_objs)):
        l_shp_file.line(line_objs[i])
        l_shp_file.record(line_attr[i])
    a_shp_file.close
    l_shp_file.close
print('Done.')
